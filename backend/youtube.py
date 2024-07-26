import datetime
import json
import re
from pytube import YouTube


def get_likes(pytube_instance):
    like_template = r"like this video along with (.*?) other people"
    text = str(pytube_instance.initial_data)
    matches = re.findall(like_template, text, re.MULTILINE)
    if len(matches) >= 1:
        like_str = matches[0] 
        return int(like_str.replace(',', ''))
    return False

def get_video_details(url):
    try:
        yt = YouTube(url)
        title = yt.title
        description = yt.description
        video_length = yt.length  # in seconds
        views = yt.views
        try:
            captions = {
                    lang: yt.captions[lang].generate_srt_captions() 
                    for lang in yt.captions
            }

        except Exception as e:
            catptions = {}

        upload_date = yt.publish_date.strftime('%Y-%m-%d') if yt.publish_date else ""
        channel_name = yt.author
        likes = get_likes(yt)

        return {
            "title": title,
            "description": description,
            "video_length": video_length,
            "views": views,
            "captions": captions,
            "upload_date": upload_date,
            "channel_name": channel_name,
            "likes": int(likes) if likes else 0,
        }
    except Exception as e:
        return {}

def get_config():
    with open("./config.json", "r") as f:
        return json.load(f)

def filter_video(video_info, config):
    inf = float('inf')
    ret = True
    # Filter by channel name
    if video_info["channel_name"] in config["allowed_channels"]:
        return False
    if video_info["channel_name"] in config["disallowed_channels"]:
        return True
    
    # TODO filer by topic

    if config["max_video_length"] == -1:
        config["max_video_length"] = inf

    if config["max_views"] == -1:
        config["max_views"] = inf

    if config["max_likes"] == -1:
        config["max_likes"] = inf

    # Filter by video length
    if not (config["min_video_length"] <= video_info["video_length"] <= config["max_video_length"]):
        return True
    
    # Filter by views
    if not config["min_views"] <= video_info["views"] <= config["max_views"]:
        return True

    # Filter by likes
    if not config["min_likes"] <= video_info["likes"] <= config["max_likes"]:
        return True

    # Filter by upload date
    current_time = datetime.datetime.now()
    uploaded = datetime.datetime.strptime(video_info["upload_date"],"%Y-%m-%d")
    hours_since_upload = (current_time - uploaded).total_seconds() / 3600
    if not hours_since_upload > config["allow_hours_after_uploaded"]:
        return True
    if not hours_since_upload > config["disallow_days_after_uploaded"] * 24:
        return True
    
    return False
