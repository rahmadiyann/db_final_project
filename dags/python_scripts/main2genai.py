from typing import Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import google.generativeai as genai
import json
from datetime import date, datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from airflow.hooks.base import BaseHook

def get_db_session():
    """Create a database session using Airflow connection"""
    conn = BaseHook.get_connection('main_postgres')
    engine = create_engine(f'postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}')
    Session = sessionmaker(bind=engine)
    return Session()

def default_serializer(obj):
    if isinstance(obj, (date,)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def handle_data(session, model, fields):
    data = []
    for record in session.query(model).all():
        data.append({field: getattr(record, field) for field in fields})
    return data

def source2landing(ArtistLongestStreak, AlbumCompletionAnalysis, AlbumReleaseYearPlayCount, LongestListeningDay, DayOfWeekListeningDistribution, HourOfDayListeningDistribution, Statistics, TopPlayedSong, SessionBetweenSongs, SongDurationPreference, SongPopularityDistribution, ExplicitPreference):
    session = get_db_session()
    data = {
        'artist_longest_streak': handle_data(session, ArtistLongestStreak, [
            'artist_id', 'artist_name', 'artist_image_url', 'streak_days', 'date_from', 'date_until'
        ]),
        'album_completion_analysis': handle_data(session, AlbumCompletionAnalysis, [
            'album_title', 'artist_name', 'album_image_url', 'total_tracks', 'unique_tracks_played',
            'completion_percentage', 'listening_status'
        ]),
        'album_release_year_play_count': handle_data(session, AlbumReleaseYearPlayCount, [
            'release_year', 'play_count'
        ]),
        'longest_listening_day': handle_data(session, LongestListeningDay, [
            'date', 'total_miliseconds', 'songs_played'
        ]),
        'day_of_week_listening_distribution': handle_data(session, DayOfWeekListeningDistribution, [
            'day_of_week', 'play_count', 'unique_songs', 'unique_artists', 'song_variety_percentage',
            'artist_variety_percentage'
        ]),
        'hour_of_day_listening_distribution': handle_data(session, HourOfDayListeningDistribution, [
            'hour_of_day', 'play_count', 'percentage'
        ]),
        'statistics': handle_data(session, Statistics, [
            'total_miliseconds', 'total_songs_played'
        ]),
        'top_played_song': handle_data(session, TopPlayedSong, [
            'song_id', 'song_title', 'artist_id', 'artist_name', 'artist_image_url', 'play_count',
            'first_played_at', 'last_played_at'
        ]),
        'session_between_songs': handle_data(session, SessionBetweenSongs, [
            'session_type', 'count', 'percentage'
        ]),
        'song_duration_preference': handle_data(session, SongDurationPreference, [
            'duration_category', 'play_count', 'percentage'
        ]),
        'song_popularity_distribution': handle_data(session, SongPopularityDistribution, [
            'popularity_bracket', 'play_count', 'popularity_range', 'percentage'
        ]),
        'explicit_preference': handle_data(session, ExplicitPreference, [
            'explicit', 'play_count', 'percentage'
        ])
    }
    
    try:
        data_dir = '/data/monthly_email_blast/landing'
        os.makedirs(data_dir, exist_ok=True)
        date_now = datetime.now().strftime('%Y-%m-%d')
        data_file = os.path.join(data_dir, f'data_{date_now}.json')
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2, default=default_serializer)
        return data_file
    finally:
        session.close()

def sendEmail(email_file: str):
    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_receiver = os.getenv('EMAIL_RECEIVER')
    with open(email_file, 'r') as f:
        message = f.read()
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = 'Your Music Universe'
    msg.attach(MIMEText(message, 'html'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_receiver, msg.as_string())
        server.quit()
        print('Email sent successfully')
        return {
            'status': 'success',
            'message': 'Email sent successfully'
        }
    except Exception as e:
        print(e)
        return {
            'status': 'error',
            'message': str(e)
        }
        
def generate_content(data_file: str) -> Dict[str, Any]:
    """Generates content using the Gemini 1.5 Flash model.

    Args:
        data: The dictionary of spotify listening history data.

    Returns:
        A dictionary containing the generated content.
    """
    genai.configure(api_key=os.getenv('GENAI_API'))
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    system_instruction = """
        You are an expert music and/or song analyst.
        Given an dictionary of spotify listening history data, I need you to generate a monthly recap summary, mood recap, and recommendations. 
        You are to start and end your response with a fun and engaging opening and closing statement.
        Your responses should be engaging and fun to read, also use emojis where necessary.
        For song name, and artist name in the recaps, wrap it inside '' as I don't want you to return a markdown.
        Return only the raw JSON without any markdown formatting or code blocks.
        Your response should be returned in json format like this:
        {
            "opening_statement": opening_statement,
            "monthly_recap": monthly_recap,
            "mood_recap": mood_recap,
            "recommendations": recommendations,
            "closing_statement": closing_statement
        }
    """
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
    prompt = f"""
    User input: {data}
    Answer:
    """
    try:
        response = model.generate_content(
            contents=prompt
        )
        content_response = response.text
        print(f"Content generation successful")
        print(f"Content response: {content_response}")
        
        # Clean up the response - remove markdown code blocks if present
        content_response = content_response.strip()
        if content_response.startswith('```'):
            # Remove the first line (```json or similar)
            content_response = '\n'.join(content_response.split('\n')[1:])
        if content_response.endswith('```'):
            # Remove the last line (```)
            content_response = '\n'.join(content_response.split('\n')[:-1])
        
        content_response = content_response.strip()
        if not content_response:
            raise ValueError("Empty response received from model")
            
        try:
            parsed_response = json.loads(content_response)
            # Verify all required keys are present
            required_keys = ['opening_statement', 'monthly_recap', 'mood_recap', 
                           'recommendations', 'closing_statement']
            missing_keys = [key for key in required_keys if key not in parsed_response]
            
            if missing_keys:
                raise ValueError(f"Missing required keys in response: {missing_keys}")
                
            data_dir = '/data/monthly_email_blast/staging'
            os.makedirs(data_dir, exist_ok=True)
            date_now = datetime.now().strftime('%Y-%m-%d')
            content_file = os.path.join(data_dir, f'ai_content_{date_now}.json')
            with open(content_file, 'w') as f:
                json.dump(parsed_response, f, indent=2)
            return content_file
            
        except json.JSONDecodeError as json_error:
            print(f"Failed to parse JSON response: {json_error}")
            raise ValueError(f"Invalid JSON response: {content_response}")
            
    except Exception as error:
        print(f"Error generating content: {error}")
        return {
            "error": str(error),
            "raw_response": content_response if 'content_response' in locals() else None
        }
        
def format_ai_content(content_dict):
    """Format the AI content from dictionary format to readable text"""
    if isinstance(content_dict, str):
        return content_dict
    
    if isinstance(content_dict, dict):
        return ' '.join(str(value) for value in content_dict.values())
    
    if isinstance(content_dict, list):
        formatted_items = []
        for item in content_dict:
            if isinstance(item, dict):
                # Format each recommendation item
                parts = []
                if 'artist' in item:
                    parts.append(f"• {item['artist']}")
                if 'album' in item:
                    parts.append(f"• {item['album']}")
                if 'genre' in item:
                    parts.append(f"• {item['genre']}")
                if 'reason' in item:
                    parts.append(f"  {item['reason']}")
                formatted_items.append('\n'.join(parts))
            else:
                formatted_items.append(str(item))
        return '\n\n'.join(formatted_items)
    
    return str(content_dict)

def ingest_email_content(data_file: str, content_file: str):
    # Read the AI-generated content and data
    with open(content_file, 'r') as f:
        content = json.load(f)
    with open(data_file, 'r') as f:
        data = json.load(f)
        
    airflow_dir = '/opt/airflow/dags'
    
    # Get current month name
    current_month = datetime.now().strftime('%B')
    
    # Read the email template
    with open(f'{airflow_dir}/python_scripts/email.html', 'r') as f:
        email_template = f.read()

    # Create a BeautifulSoup object to parse and modify the HTML
    soup = BeautifulSoup(email_template, 'html.parser')
    
    # Update the month in the header
    month_text = soup.find('span', {'id': 'current-month'})
    if month_text:
        month_text.string = current_month
    
    # Add opening statement first
    opening_div = soup.find(id='opening-statement')
    if opening_div and 'opening_statement' in content:
        opening_section = soup.new_tag('div')
        opening_section['class'] = "card-bg rounded-xl p-6 border border-gray-700 text-center"
        
        content_tag = soup.new_tag('p')
        content_tag['class'] = 'text-xl text-gray-300 leading-relaxed'
        content_tag.string = format_ai_content(content.get('opening_statement', ''))
        
        opening_section.append(content_tag)
        opening_div.clear()
        opening_div.append(opening_section)

    # Add data visualization sections first
    stats_sections = {
        'top-played-song-data': {
            'title': '🎵 Top Played Track',
            'content': create_top_song_section(data['top_played_song'][0]),
            'classes': 'bg-gradient-to-r from-indigo-50 to-blue-50 border-l-4 border-indigo-500'
        },
        'longest-listening-day-data': {
            'title': '📅 Peak Listening Day',
            'content': create_listening_day_section(data['longest_listening_day'][0]),
            'classes': 'bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500'
        },
        'artist-streak-data': {
            'title': '🎸 Artist Streak',
            'content': create_artist_streak_section(data['artist_longest_streak'][0]),
            'classes': 'bg-gradient-to-r from-purple-50 to-violet-50 border-l-4 border-purple-500'
        },
        'listening-habits-data': {
            'title': '📊 Listening Habits',
            'content': create_listening_habits_section(data),
            'classes': 'bg-gradient-to-r from-orange-50 to-amber-50 border-l-4 border-orange-500'
        }
    }

    # Add data sections
    for section_id, section_info in stats_sections.items():
        section_div = soup.find(id=section_id)
        if section_div:
            section_div['class'] = f"mb-8 rounded-lg shadow-sm overflow-hidden {section_info['classes']}"
            
            # Create inner container
            inner_div = soup.new_tag('div')
            inner_div['class'] = 'p-6'
            
            # Add title
            title_tag = soup.new_tag('h2')
            title_tag['class'] = 'text-2xl font-bold text-gray-800 mb-4 flex items-center'
            title_tag.string = section_info['title']
            inner_div.append(title_tag)
            
            # Add content - parse HTML string into BeautifulSoup objects
            content_html = BeautifulSoup(section_info['content'], 'html.parser')
            inner_div.append(content_html)
            
            section_div.clear()
            section_div.append(inner_div)

    # Modify AI analysis sections to exclude opening statement
    ai_analysis_div = soup.find(id='ai-analysis')
    if ai_analysis_div:
        container = soup.new_tag('div')
        container['class'] = 'space-y-8 px-4'
        
        sections = {
            'monthly_recap': {
                'title': '📊 Monthly Recap',
                'content': format_ai_content(content.get('monthly_recap', '')),
                'classes': 'bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500'
            },
            'mood_recap': {
                'title': '🎵 Mood Analysis',
                'content': format_ai_content(content.get('mood_recap', '')),
                'classes': 'bg-gradient-to-r from-green-50 to-teal-50 border-l-4 border-green-500'
            },
            'recommendations': {
                'title': '🎧 Recommended for You',
                'content': format_ai_content(content.get('recommendations', '')),
                'classes': 'bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-yellow-500'
            },
            'closing_statement': {
                'title': '👋 Until Next Time',
                'content': format_ai_content(content.get('closing_statement', '')),
                'classes': 'bg-gradient-to-r from-red-50 to-pink-50 border-l-4 border-red-500'
            }
        }
        
        for section_id, section_info in sections.items():
            section_div = soup.new_tag('div')
            section_div['class'] = f"rounded-lg shadow-sm overflow-hidden {section_info['classes']} transition-all duration-300 hover:shadow-md"
            
            inner_div = soup.new_tag('div')
            inner_div['class'] = 'p-6'
            
            title_tag = soup.new_tag('h2')
            title_tag['class'] = 'text-2xl font-bold text-gray-800 mb-4 flex items-center'
            title_tag.string = section_info['title']
            inner_div.append(title_tag)
            
            content_tag = soup.new_tag('div')
            content_tag['class'] = 'text-gray-600 leading-relaxed space-y-2'
            
            if section_id == 'recommendations':
                # Handle recommendations as a list
                for line in section_info['content'].split('\n'):
                    if line.strip():
                        p_tag = soup.new_tag('p')
                        p_tag.string = line.strip()
                        content_tag.append(p_tag)
            else:
                # Create a paragraph for the content
                p_tag = soup.new_tag('p')
                p_tag.string = section_info['content']
                content_tag.append(p_tag)
            
            inner_div.append(content_tag)
            section_div.append(inner_div)
            container.append(section_div)
        
        ai_analysis_div.clear()
        ai_analysis_div.append(container)

    # Save the modified HTML
    data_dir = '/data/monthly_email_blast/staging'
    os.makedirs(data_dir, exist_ok=True)
    date_now = datetime.now().strftime('%Y-%m-%d')
    email_file = os.path.join(data_dir, f'email_{date_now}.html')
    
    with open(email_file, 'w') as f:
        f.write(str(soup))
    
    return email_file

def create_top_song_section(song_data):
    return f"""
    <div class="card-bg rounded-xl p-6 transform transition-all duration-300 hover:scale-105 border border-gray-700">
        <div class="flex items-center space-x-6">
            <div class="relative">
                <div class="absolute inset-0 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full animate-pulse opacity-30"></div>
                <img src="{song_data['artist_image_url']}" alt="{song_data['artist_name']}" 
                     class="w-24 h-24 rounded-full shadow-xl relative z-10 hover-pulse">
            </div>
            <div class="flex-1">
                <h3 class="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400">
                    {song_data['song_title']}
                </h3>
                <p class="text-lg text-gray-300">{song_data['artist_name']}</p>
                <div class="mt-2 flex items-center">
                    <span class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-pink-400">
                        {song_data['play_count']}
                    </span>
                    <span class="ml-2 text-gray-300">times played</span>
                </div>
            </div>
        </div>
    </div>
    """

def create_listening_day_section(day_data):
    hours = day_data['total_miliseconds'] / (1000 * 60 * 60)
    return f"""
    <div class="card-bg rounded-xl p-6 transform transition-all duration-300 hover:scale-105 border border-gray-700">
        <h3 class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-teal-400 mb-4">
            Peak Listening Marathon
        </h3>
        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <span class="text-gray-300">Date</span>
                <span class="text-xl font-bold text-white">{day_data['date']}</span>
            </div>
            <div class="flex items-center justify-between">
                <span class="text-gray-300">Hours Vibing</span>
                <div class="flex items-baseline">
                    <span class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-teal-400">
                        {hours:.1f}
                    </span>
                    <span class="ml-2 text-gray-300">hours</span>
                </div>
            </div>
            <div class="flex items-center justify-between">
                <span class="text-gray-300">Track Count</span>
                <div class="flex items-baseline">
                    <span class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-teal-400">
                        {day_data['songs_played']}
                    </span>
                    <span class="ml-2 text-gray-300">songs</span>
                </div>
            </div>
        </div>
    </div>
    """

def create_artist_streak_section(streak_data):
    return f"""
    <div class="card-bg rounded-xl p-6 transform transition-all duration-300 hover:scale-105 border border-gray-700">
        <div class="flex items-center space-x-6">
            <div class="relative">
                <div class="absolute inset-0 bg-gradient-to-r from-yellow-500 to-red-500 rounded-full animate-pulse opacity-30"></div>
                <img src="{streak_data['artist_image_url']}" alt="{streak_data['artist_name']}" 
                     class="w-24 h-24 rounded-full shadow-xl relative z-10 hover-pulse">
            </div>
            <div class="flex-1">
                <h3 class="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-red-400">
                    {streak_data['artist_name']}
                </h3>
                <div class="mt-2">
                    <span class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-red-400">
                        {streak_data['streak_days']}
                    </span>
                    <span class="ml-2 text-gray-300">day streak 🔥</span>
                </div>
                <p class="text-sm text-gray-300 mt-2">
                    From {streak_data['date_from']} to {streak_data['date_until']}
                </p>
            </div>
        </div>
    </div>
    """

def create_listening_habits_section(data):
    explicit = data['explicit_preference']
    duration = data['song_duration_preference']
    
    return f"""
    <div class="card-bg rounded-xl p-6 transform transition-all duration-300 hover:scale-105 border border-gray-700">
        <h3 class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400 mb-6">
            Your Music DNA 🧬
        </h3>
        <div class="grid grid-cols-1 gap-6">
            <div class="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
                <h4 class="font-semibold text-lg text-blue-300 mb-3">Track Length Preference</h4>
                <div class="space-y-3">
                    {create_percentage_bars(duration, 'duration_category', 'percentage')}
                </div>
            </div>
            <div class="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
                <h4 class="font-semibold text-lg text-blue-300 mb-3">Content Rating</h4>
                <div class="space-y-3">
                    <div class="flex items-center justify-between">
                        <span class="text-gray-300">Clean</span>
                        <div class="flex items-baseline">
                            <span class="text-2xl font-bold text-blue-400">
                                {next(item['percentage'] for item in explicit if not item['explicit']):.1f}%
                            </span>
                        </div>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-gray-300">Explicit</span>
                        <div class="flex items-baseline">
                            <span class="text-2xl font-bold text-red-400">
                                {next(item['percentage'] for item in explicit if item['explicit']):.1f}%
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def create_percentage_bars(data, label_key, percentage_key):
    sorted_data = sorted(data, key=lambda x: x[percentage_key], reverse=True)
    bars = []
    for item in sorted_data:
        percentage = item[percentage_key]
        bars.append(f"""
            <div>
                <div class="flex justify-between mb-1">
                    <span class="text-gray-300">{item[label_key]}</span>
                    <span class="text-blue-400 font-semibold">{percentage:.1f}%</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2.5">
                    <div class="bg-gradient-to-r from-blue-400 to-indigo-400 h-2.5 rounded-full"
                         style="width: {percentage}%"></div>
                </div>
            </div>
        """)
    return '\n'.join(bars)
