import streamlit as st
import instaloader
import os
import re
import shutil

# extract Shortcode 
def get_shortcode_from_url(url):
    """Extracts the shortcode from an Instagram URL."""
    match = re.search(r"(?:p|reel|tv)/([\w-]+)", url)
    if match:
        return match.group(1)
    return None

# Download Logic
def process_and_download(url):
    """Handles the entire download process for a given URL."""
    if not url:
        st.warning("Please provide an Instagram Reel URL.")
        return

    shortcode = get_shortcode_from_url(url)
    if not shortcode:
        st.error("Invalid Instagram Reel URL. Please enter a valid URL.")
        return

    try:
        with st.spinner('Processing URL... Please wait.'):
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Use shortcode for a unique, temporary directory
            target_dir = f"downloads_{shortcode}"
            
            # Download the post media
            L.download_post(post, target=target_dir)

            # Find the downloaded video file
            video_file = None
            for filename in os.listdir(target_dir):
                if filename.endswith(".mp4"):
                    video_file = os.path.join(target_dir, filename)
                    break
            
            if video_file:
                st.success("Reel loaded successfully!, \n Click on Download Video to Save it into your device.")

                video_bytes = open(video_file, 'rb').read()
                
                st.download_button(
                    label="Download Video",
                    icon=":material/download:",
                    data=video_bytes,
                    file_name=f"{shortcode}.mp4",
                    mime="video/mp4",
                    type='primary'
                )

                st.video(video_bytes)

            else:
                st.error("Could not find a video file. The post might not be a reel.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error("This could be due to a private account, an invalid URL, or Instagram's rate limiting.")
    
    finally:
        # Clean up the downloaded files from the server
        if 'target_dir' in locals() and os.path.exists(target_dir):
            shutil.rmtree(target_dir)


# Streamlit App UI
st.set_page_config(page_title="Instagram Reel Downloader", page_icon="Reels Video Downloader", layout="centered")
st.header("Instagram Reel Downloader", divider=True)


# This checks if a 'url' parameter exists in the app's web address
query_params = st.query_params
if "url" in query_params:
    url_from_query = query_params["url"]
    st.info(f"Processing URL from query parameter: {url_from_query}")
    process_and_download(url_from_query)
else:
    # Default UI if no URL parameter is found
    st.markdown("Enter the URL of the Instagram Reel you want to download below.")

    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        url_from_input = st.text_input("Instagram Reel/Post URL:", placeholder="https://www.instagram.com/reel/C1_AbCd...")
    
    with col2:
        if st.button("Go", type="primary"):
            process_and_download(url_from_input)

    st.markdown("---")
    st.markdown("**Note:** Please make sure Reel/Video is public to download" )