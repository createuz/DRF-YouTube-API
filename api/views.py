from rest_framework.decorators import api_view
from rest_framework.response import Response
from httpx import AsyncClient
from django.shortcuts import redirect
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')


@api_view(['GET'])
def root(request):
    return redirect('/docs')


@api_view(['GET'])
def get_video(request, video_id):
    result = get_video_data(video_id)
    if result:
        return Response(result)

    return Response({'message': f'Video with id {video_id} not found.'}, status=404)


@api_view(['GET'])
def get_channel(request, channel_id):
    result = get_channel_data(channel_id)
    if result:
        return Response(result)

    return Response({'message': f'Channel with id {channel_id} not found.'}, status=404)


async def get_video_data(video_id):
    try:
        async with AsyncClient() as client:
            url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics'
            data = {'id': video_id, 'key': API_KEY}
            r = await client.get(url, params=data)

            if r.status_code != 200:
                return False

            video = r.json()['items'][0]

            return {
                'title': video['snippet'].get('title'),
                'channelId': video['snippet'].get('channelId'),
                'description': video['snippet'].get('description'),
                'keywords': video['snippet'].get('tags'),
                'publishedAt': video['snippet'].get('publishedAt').replace('T', ' ').replace('Z', ' '),
                'duration': video['contentDetails'].get('duration').replace('M', 'M ').replace('PT', ''),
                'thumbnails': video['snippet']['thumbnails']['default']['url'],
                'viewCount': video['statistics'].get('viewCount'),
                'likeCount': video['statistics'].get('likeCount'),
                'commentCount': video['statistics'].get('commentCount')
            }
    except KeyError:
        return False


async def get_channel_data(channel_id):
    try:
        async with AsyncClient() as client:
            url = 'https://www.googleapis.com/youtube/v3/channels'
            data = {'part': 'statistics,brandingSettings', 'id': channel_id, 'key': API_KEY}
            r = await client.get(url, params=data)
            if r.status_code != 200:
                return False
            statistics = r.json()['items'][0]['statistics']
            branding = r.json()['items'][0]['brandingSettings']
        return {
            'title': branding['channel'].get('title'),
            'description': branding['channel'].get('description'),
            'keywords': branding['channel'].get('keywords'),
            'country': branding['channel'].get('country'),
            'bannerExternalUrl': branding['image'].get('bannerExternalUrl'),
            'unsubscribedTrailer': 'https://www.youtube.com/watch?v=' + branding['channel'].get(
                'unsubscribedTrailer') if branding['channel'].get('unsubscribedTrailer') else 'None',
            'id': channel_id,
            'url': 'https://www.youtube.com/channel/' + channel_id,
            'videoCount': statistics.get('videoCount'),
            'viewCount': statistics.get('viewCount'),
            'subscriberCount': statistics.get('subscriberCount'),
            'hiddenSubscriberCount': statistics.get('hiddenSubscriberCount')
        }
    except KeyError:
        return False
