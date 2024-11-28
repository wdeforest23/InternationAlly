import streamlit as st
import time
import os
from dotenv import load_dotenv
from settings import setup, configure_display_options
from chatbot import chat_all
from map_creation import get_default_chicago_map_config, render_map

# Load the API key for Google Maps from .env
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("PROD_GOOGLE_MAP_API_KEY")

# Page configuration
st.set_page_config(page_title="InternationAlly", page_icon="ally-logo.png", layout="centered")

# Custom CSS for styling font, colors, and form layout
st.markdown("""
    <style>

        [data-testid=stSidebar] {
        background-color: #ffffff;
        }

        /* Change the font family and colors for the main app */
        html, body, [class*="css"]  {
            font-family: 'Open Sans', sans-serif !important;
            color: #333333;  /* Main text color */

        }

        /* Center title styling */
        .main-title {
            color: #434343;
            font-family: 'Open Sans', sans-serif !important;
            font-size: 42px;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
        }

        /* Form styling */
        .form-container {
            margin-top: 100px;
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }

        button {
            height: auto;
            padding-top: 15px !important;
            padding-bottom: 15px !important;
            margin-bottom: -5px !important;
        }

        /* Customize button colors */
        .stButton>button {
            color: #FFFFFF !important; 
            background-color: #9AD6D2 !important;
            border: none;
            margin-top: 10px;
            padding: 8px 16px;
            font-weight: bold;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #86cec9 !important;  /* Darker on hover */
            color: #FFFFFF !important;
        }
        .stButton>button:active {
            background-color: #86cec9 !important; /* Keep the same background color when clicked */
            color: #FFFFFF !important;  /* Keep the text color white when clicked */
        }
         
        /* Input field styling */
        .stTextInput, .stPasswordInput {
            background-color: #ffffff;
            border-radius: 4px;
            padding: 0px;
            width: 100%;
            margin-top: 0px;
        }

        /* Link styling */
        .signup-link {
            text-align: center;
            margin-top: 20px;
            font-weight: bold;
            font-size: 20px;
        }
            
        /* Success message box */
        .st-success-box {
            color: #55555C;
            background-color: #FFF8E8;
            padding: 10px;
            border-radius: 1px;
            font-weight: bold;
            margin: 10px 0;
        }

        /* Error message box */
        .st-error-box {
            color: #55555C;
            background-color: #F4E5E3;
            padding: 10px;
            border-radius: 1px;
            font-weight: bold;
            margin: 10px 0;
        }
            
        /* Adjust the height of input fields */
        input[type="text"], input[type="password"] {
            height: 55px;              /* Sets a fixed height */
            font-size: 18px;           /* Increases the font size */
            width: 100%;               /* Makes input full-width of its container */
            padding: 12px;             /* Adds space inside the input for a larger clickable area */
            color: #333333;            /* Sets text color */
            /* background-color: #f9f9f9; Sets background color of input */
            border-radius: 1px;        /* Rounds the corners */
            outline: none;             /* Removes the default outline when input is focused */
            box-shadow: none;          /* Removes default box shadow */
            transition: all 0.3s ease; /* Adds a smooth transition for hover or focus effects */
        }
            
        .css-1d391kg {  /* This class targets the sidebar in Streamlit */
            top: 0;
            left: 0;
            height: 100vh;
            background-color: #ffffff;
            padding-top: 1rem;
            z-index: 100;
            width: 100px;  /* Set the desired sidebar width here */
        }
        
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if "users" not in st.session_state:
    st.session_state.users = {"user1": {"password": "password1"}, "user2": {"password": "password2"}}
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}  # To store chat histories per user
if "current_map_html" not in st.session_state:
    # Set the initial map to be centered on Chicago
    default_map_config = get_default_chicago_map_config()
    st.session_state.current_map_html = render_map(GOOGLE_MAPS_API_KEY, **default_map_config)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "show_onboarding" not in st.session_state:
    st.session_state.show_onboarding = False
if "user_onboarding_data" not in st.session_state:
    st.session_state.user_onboarding_data = {}
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1  # Start at step 1


# Toggle the sign-up page
def show_signup():
    st.session_state.show_signup = True

# Toggle the login page
def show_login():
    st.session_state.show_signup = False

import base64

# Function to load and convert an image file to base64 string
def load_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

import re

def onboarding_page():
    # Load and convert the logo image
    logo_base64 = load_image_as_base64("ally-logo.png")  # Ensure the path is correct

    # Display the centered logo using HTML and Base64
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 5px;">
            <img src="data:image/jpg;base64,{logo_base64}" width="80">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='main-title'>InternationAlly by PropertyPilot</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display: flex; justify-content: center; text-align: center; margin-top: 1px;">
            <p style="font-size: 30px;">Your Ally Abroad! 🚀</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    current_user = st.session_state.current_user
    first_name = st.session_state.users[current_user]["first_name"]

    # Step 1: Ask about the user's origin
    if st.session_state.onboarding_step == 1:
        st.markdown(f"<div style='text-align: center; font-size: 30px;'>Hey {first_name}, let's get to know you better!</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px; margin-top: 20px; margin-bottom: 5px;'>Where are you from, {first_name}?</div>", unsafe_allow_html=True)
        
        # Input for place of origin
        place_of_origin = st.text_input("Your hometown or country:", key="place_of_origin", label_visibility="collapsed", placeholder="Enter your hometown or country")
        
        # Next button to proceed to the second step
        if st.button("Next"):
            if place_of_origin.strip():  # Ensure the user entered something
                # Save the response
                st.session_state.user_onboarding_data[current_user] = {
                    "place_of_origin": place_of_origin.strip()
                }
                st.session_state.onboarding_step = 2  # Move to the next step
                st.experimental_rerun()
            else:
                st.markdown("<div class='st-error-box'>❗ Please tell us where you're from to proceed.</div>", unsafe_allow_html=True)

    # Step 2: Ask about the city the user is moving to
    elif st.session_state.onboarding_step == 2:
        st.markdown(f"<div style='text-align: center; font-size: 30px;'>Hey {first_name}, let's get to know you better!</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px; margin-top: 20px; margin-bottom: 5px;'>Which city are you moving to in the US?</div>", unsafe_allow_html=True)
        
        # Input for city in the US
        us_city = st.text_input("Your destination city in the US:", key="us_city", label_visibility="collapsed", placeholder="Enter the city name")

        # Finish Sign Up button
        if st.button("Next"):
            if us_city.strip():  # Ensure the user entered something
                # Save the response
                st.session_state.user_onboarding_data[current_user]["us_city"] = us_city.strip()
                st.session_state.onboarding_step = 3  # Move to the next step
                st.experimental_rerun()
            else:
                st.markdown("<div class='st-error-box'>❗ Please tell us your destination city to complete the onboarding.</div>", unsafe_allow_html=True)

    # Step 3: Ask about the college the user is attending
    elif st.session_state.onboarding_step == 3:
        st.markdown(f"<div style='text-align: center; font-size: 30px;'>Hey {first_name}, let's get to know you better!</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px; margin-top: 20px; margin-bottom: 5px;'>Which school are you attending in the US?</div>", unsafe_allow_html=True)
        
        # Input for city in the US
        us_college = st.text_input("Your school/college:", key="us_college", label_visibility="collapsed", placeholder="Enter the school/college name")

        # Finish Sign Up button
        if st.button("Next"):
            if us_college.strip():  # Ensure the user entered something
                # Save the response
                st.session_state.user_onboarding_data[current_user]["us_college"] = us_college.strip()
                st.session_state.onboarding_step = 4  # Move to the next step
                st.experimental_rerun()
            else:
                st.markdown("<div class='st-error-box'>❗ Please tell us your school/college to complete the onboarding.</div>", unsafe_allow_html=True)

    # Step 4
    elif st.session_state.onboarding_step == 4:
        st.markdown(f"<div style='text-align: center; font-size: 30px;'>Hey {first_name}, let's get to know you better!</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px; margin-top: 20px; margin-bottom: 5px;'>Do you have a student health insurance?</div>", unsafe_allow_html=True)
        
        # Input for city in the US
        us_insurance = st.text_input("Do you have a student health insurance?:", key="us_insurance", label_visibility="collapsed", placeholder="Do you have a student health insurance? (Yes/No)")

        # Finish Sign Up button
        if st.button("Next"):
            if us_insurance.strip():  # Ensure the user entered something
                # Save the response
                st.session_state.user_onboarding_data[current_user]["us_insurance"] = us_insurance.strip()
                st.session_state.onboarding_step = 5  # Move to the next step
                st.experimental_rerun()
            else:
                st.markdown("<div class='st-error-box'>❗ Please tell us your whether you have a student health insurance so that Ally could better serve you.</div>", unsafe_allow_html=True)

    # Step 5
    elif st.session_state.onboarding_step == 5:
        st.markdown(f"<div style='text-align: center; font-size: 30px;'>Hey {first_name}, let's get to know you better!</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px; margin-top: 20px; margin-bottom: 5px;'>Do you have a Social Security Number?</div>", unsafe_allow_html=True)
        
        # Input for city in the US
        us_ssn = st.text_input("Do you have a Social Security Number?:", key="us_ssn", label_visibility="collapsed", placeholder="Do you have a Social Security Number? (Yes/No)")

        # Finish Sign Up button
        if st.button("Next"):
            if us_ssn.strip():  # Ensure the user entered something
                # Save the response
                st.session_state.user_onboarding_data[current_user]["us_ssn"] = us_ssn.strip()
                st.session_state.onboarding_step = 6  # Move to the next step
                st.experimental_rerun()
            else:
                st.markdown("<div class='st-error-box'>❗ Please tell us your whether you have a Social Security Number so that Ally could better serve you.</div>", unsafe_allow_html=True)

    # Step 6
    elif st.session_state.onboarding_step == 6:
        st.markdown(f"<div style='text-align: center; font-size: 30px;'>Hey {first_name}, let's get to know you better!</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px; margin-top: 20px; margin-bottom: 5px;'>Did you find a place to stay in the US?</div>", unsafe_allow_html=True)
        
        # Input for city in the US
        us_place_to_stay = st.text_input("Did you find a place to stay in the US?", key="us_place_to_stay", label_visibility="collapsed", placeholder="Did you find a place to stay in the US?")

        # Finish Sign Up button
        if st.button("Next"):
            if us_place_to_stay.strip():  # Ensure the user entered something
                # Save the response
                st.session_state.user_onboarding_data[current_user]["us_place_to_stay"] = us_place_to_stay.strip()
                st.session_state.onboarding_step = 7  # Move to the next step
                st.experimental_rerun()
            else:
                st.markdown("<div class='st-error-box'>❗ Ally could help you with searching for rental properties if you let us know.</div>", unsafe_allow_html=True)


    # Step 7
    elif st.session_state.onboarding_step == 7:
        st.markdown(f"<div style='text-align: center; font-size: 30px;'>Almost there, {first_name}!</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 20px; margin-top: 20px; margin-bottom: 5px;'>Write anything about yourself which you think would be useful for Ally to help you better.</div>", unsafe_allow_html=True)
        
        # Input for city in the US
        us_other = st.text_input("Write about yourself:", key="us_other", label_visibility="collapsed", placeholder="About you")

        # Finish Sign Up button
        if st.button("Finish Sign Up"):
            if us_other.strip():  # Ensure the user entered something
                # Save the response
                st.session_state.user_onboarding_data[current_user]["us_other"] = us_other.strip()
                # Redirect to login page
                st.session_state.show_onboarding = False
                st.session_state.show_signup = False
                st.session_state.onboarding_step = 1  # Move to the next step
                st.experimental_rerun()
            else:
                st.markdown("<div class='st-error-box'>❗ Although it's totally optional, please tell us about yourself. 🤗</div>", unsafe_allow_html=True)


# Function for the Sign-Up page
def signup_page():
    # Load and convert the logo image
    logo_base64 = load_image_as_base64("ally-logo.png")  # Ensure the path is correct

    # Display the centered logo using HTML and Base64
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 5px;">
            <img src="data:image/jpg;base64,{logo_base64}" width="80">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='main-title'>InternationAlly by PropertyPilot</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display: flex; justify-content: center; text-align: center; margin-top: 1px;">
            <p style="font-size: 30px;">Your Ally Abroad! 🚀</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="display: flex; justify-content: center; text-align: center; margin-top: 20px;">
            <p style="font-size: 18px;">Create an account to access Ally, your trusted international student advisor.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form(key='signup_form'):

        # New fields for user details
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>First Name</p>", unsafe_allow_html=True)
        first_name = st.text_input("First Name", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Last Name</p>", unsafe_allow_html=True)
        last_name = st.text_input("Last Name", label_visibility="collapsed")

        # New field for email
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Email</p>", unsafe_allow_html=True)
        email = st.text_input("Email", label_visibility="collapsed")

        # Existing fields for username and password
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Create a Username</p>", unsafe_allow_html=True)
        new_username = st.text_input("Create a Username", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Create a Password</p>", unsafe_allow_html=True)
        new_password = st.text_input("Create a Password", type="password", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Confirm Password</p>", unsafe_allow_html=True)
        confirm_password = st.text_input("Confirm Password", type="password", label_visibility="collapsed")

        submit_button = st.form_submit_button("Sign Up")

    if submit_button:
        # Sanity check for email format using regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        # Check if all fields are filled
        if not first_name or not last_name:
            st.markdown("<div class='st-error-box'>❗ Please fill out all personal details.</div>", unsafe_allow_html=True)
        elif not email:
            st.markdown("<div class='st-error-box'>❗ Please provide an email address.</div>", unsafe_allow_html=True)
        elif not re.match(email_pattern, email):
            st.markdown("<div class='st-error-box'>❗ Invalid email format. Please enter a valid email address.</div>", unsafe_allow_html=True)
        elif new_username in st.session_state.users:
            st.markdown("<div class='st-error-box'>❗ Username already exists. Please choose a different one.</div>", unsafe_allow_html=True)
        elif new_password != confirm_password:
            st.markdown("<div class='st-error-box'>❗ Passwords do not match.</div>", unsafe_allow_html=True)
        elif new_username and new_password and re.match(email_pattern, email):
            # Save the new user credentials and details in session state
            st.session_state.users[new_username] = {
                "password": new_password,
                "first_name": first_name,
                "last_name": last_name,
                "email": email  # Save email along with other details
            }
            st.session_state.current_user = new_username
            st.session_state.onboarding_step = 1  # Reset to the first onboarding step
            st.session_state.show_onboarding = True  # Trigger onboarding page
            st.experimental_rerun()  # Redirect to the onboarding page

        else:
            st.markdown("<div class='st-error-box'>❗ Please fill out all fields.</div>", unsafe_allow_html=True)

    # Add "Already have an account?" text and "Sign In" button below the sign-up form
    st.markdown("<div class='signup-link'>Already have an account?</div>", unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])  # To center the button
        with col2:  # Place the button in the middle column
            if st.button("Back to Sign In", key="small-backtosignin-button"):
                show_login()
                st.experimental_rerun()



# Function for the login page
def login_page():
    # Load and convert the logo image
    logo_base64 = load_image_as_base64("ally-logo.png")  # Ensure the path is correct

    # Display the centered logo using HTML and Base64
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 5px;">
            <img src="data:image/jpg;base64,{logo_base64}" width="80">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='main-title'>InternationAlly by PropertyPilot</div>", unsafe_allow_html=True)
    st.markdown(
    """
    <div style="display: flex; justify-content: center; text-align: center; margin-top: 1px;">
        <p style="font-size: 30px;">Your Ally Abroad! 🚀</p>
    </div>
    """,
    unsafe_allow_html=True
    )
    st.markdown(
    """
    <div style="display: flex; justify-content: center; text-align: center; margin-top: 20px;">
        <p style="font-size: 18px;">Sign in to get started.</p>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    # Login form container

    with st.form(key="login_form"):
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Username</p>", unsafe_allow_html=True)
        username = st.text_input("Username", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Password</p>", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", label_visibility="collapsed")
        submit_button = st.form_submit_button("Sign In")
    
    if submit_button:
        if username in st.session_state.users and st.session_state.users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username  # Track the logged-in user
            # Show success message
            st.markdown("<div class='st-success-box'>Sign-in successful ✅ Launching Ally 🤗</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.markdown("<div class='st-error-box'>❌ Invalid username or password.</div>", unsafe_allow_html=True)

    # Sign-up prompt and button for new users
    st.markdown("<div class='signup-link'>New international student?</div>", unsafe_allow_html=True)


    # Apply the custom width by wrapping the button in a container
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])  # To center the button
        with col2:  # Place the button in the middle column
            if st.button("Sign Up Here", key="small-signup-button"):
                show_signup()
                st.experimental_rerun()

# Function to edit the profile
def edit_profile_page():
    current_user = st.session_state.current_user
    first_name = st.session_state.users.get(current_user, {}).get("first_name", "")
    user_data = st.session_state.user_onboarding_data.get(current_user, {})

    st.markdown(f"<div style='text-align: center; font-size: 30px; font-weight: bold;'>Edit Your Profile, {first_name}!</div>", unsafe_allow_html=True)

    with st.form(key='edit_profile_form'):
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Your hometown or country</p>", unsafe_allow_html=True)
        place_of_origin = st.text_input("Your hometown or country:", value=user_data.get("place_of_origin", ""), key="edit_place_of_origin", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Your destination city in the US</p>", unsafe_allow_html=True)
        us_city = st.text_input("Your destination city in the US:", value=user_data.get("us_city", ""), key="edit_us_city", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Your school/college</p>", unsafe_allow_html=True)
        us_college = st.text_input("Your school/college:", value=user_data.get("us_college", ""), key="edit_us_college", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Do you have a student health insurance? (Yes/No)</p>", unsafe_allow_html=True)
        us_insurance = st.text_input("Do you have a student health insurance?", value=user_data.get("us_insurance", ""), key="edit_us_insurance", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Do you have a Social Security Number? (Yes/No)</p>", unsafe_allow_html=True)
        us_ssn = st.text_input("Do you have a Social Security Number?", value=user_data.get("us_ssn", ""), key="edit_us_ssn", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Did you find a place to stay in the US? (Yes/No)</p>", unsafe_allow_html=True)
        us_place_to_stay = st.text_input("Did you find a place to stay in the US?", value=user_data.get("us_place_to_stay", ""), key="edit_us_place_to_stay", label_visibility="collapsed")
        st.markdown("<p style='font-size:18px; font-weight:bold; color:#333333;'>Something about you</p>", unsafe_allow_html=True)
        us_other = st.text_input("About you:", value=user_data.get("us_other", ""), key="edit_us_other", label_visibility="collapsed")

        save_button = st.form_submit_button("Save Changes")

    if save_button:
        # Save the updated data to the session state
        st.session_state.user_onboarding_data[current_user] = {
            "place_of_origin": place_of_origin.strip(),
            "us_city": us_city.strip(),
            "us_college": us_college.strip(),
            "us_insurance": us_insurance.strip(),
            "us_ssn": us_ssn.strip(),
            "us_place_to_stay": us_place_to_stay.strip(),
            "us_other": us_other.strip(),
        }

        st.session_state.editing_profile = False  # Exit profile editing mode
        # st.success("Profile updated successfully!")
        st.markdown("<div class='st-success-box'>✅ Profile updated successfully!</div>", unsafe_allow_html=True)
        time.sleep(1)  # Add slight delay for better UX
        st.experimental_rerun()  # Redirect to chat screen


def chat_app():
    # Setup the bot and environment, but only once
    if 'setup_done' not in st.session_state:
        chat, prompts_dict, vectordb = setup()
        configure_display_options()
        st.session_state.chat = chat
        st.session_state.prompts_dict = prompts_dict
        st.session_state.vectordb = vectordb
        st.session_state.setup_done = True
        st.session_state.current_map_html = None  # Initialize with no map displayed

    # Ensure the current user and chat history are initialized
    current_user = st.session_state.current_user

    # Fetch the user's first name if available, default to "there"
    first_name = st.session_state.users.get(current_user, {}).get("first_name", "there")

    if current_user not in st.session_state.chat_histories:

        print(current_user)

        if (current_user == "user1") or (current_user == 'user2'):
            print("Entered.")
            st.session_state.user_onboarding_data[current_user] = {
                    "place_of_origin": 'Tokyo, Japan',
                    "us_city": 'Chicago, IL',
                    "us_college": 'The University of Chicago',
                    "us_insurance": "No",
                    "us_ssn": 'No',
                    "us_place_to_stay": "No",
                    "us_other": "I love Japanese food."
                }

        print(st.session_state.user_onboarding_data)

        from llm import start_chat_session, get_chat_response

        # Start a new chat session
        welcome_chat = start_chat_session()

        # Test the chat session with a simple prompt
        welcome_prompt = f'''Hi! You are an empathetic, polite, helpful international student advisor who helps international students with a range of services like finding them a place to stay (property search), local advising on neighborhoods and places of interest (restaurants, grocery stores, attractions, public transportation, fitness centers, etc.), and also about student essentials like health insurance, visa, etc..
        
        Based on the information the user has given so far, I want you to generate a question template like below:

        Template: Hello {first_name}! I know being an international student can feel like a lot, especially in a place like the U.S., where everything might feel new and different. How are you feeling about everything so far? Any specific areas where you’re feeling like you could use a bit of help or extra advice?

        This template should change based on the demands of the user defined through the user profile. 

        Here's the current user profile:
        User hometown: {st.session_state.user_onboarding_data[current_user]['place_of_origin']}
        User destination: {st.session_state.user_onboarding_data[current_user]['us_city']}
        User school: {st.session_state.user_onboarding_data[current_user]['us_college']}
        User have health insurance?: {st.session_state.user_onboarding_data[current_user]['us_insurance']}
        User have SSN?: {st.session_state.user_onboarding_data[current_user]['us_ssn']}
        User found a place to stay in the US?: {st.session_state.user_onboarding_data[current_user]['us_place_to_stay']}
        User other information: {st.session_state.user_onboarding_data[current_user]['us_other']}

        If the user haven't given a lot of info, you are free to make your own assumptions.

        Give one good question template as the response to me which shows an international student advisor concern towards their students.
        '''
        welcome_response = get_chat_response(welcome_chat, welcome_prompt)
        print("Response:", welcome_response)

        st.session_state.chat_histories[current_user] = [
            {
                "role": "assistant",
                "content": welcome_response,
            }
        ]
    
    # Check if the user is editing their profile
    if st.session_state.get("editing_profile", False):
        edit_profile_page()
        return

    # Sidebar content with logo, description, and buttons
    # Sidebar content with logo, description, and buttons at the bottom
    with st.sidebar:
        st.markdown(
            """
            <style>
                .sidebar-buttons {
                    position: absolute;
                    bottom: 100px; /* Adjust distance from the bottom */
                    width: calc(100% - 2rem); /* Ensure buttons take full width minus padding */
                    padding: 0 1rem;
                }
                .sidebar-content {
                    margin-bottom: 50px; /* Space to account for bottom buttons */
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        # Sidebar content above the buttons
        st.markdown(
            """
            <div class="sidebar-content">
                <div style="text-align: center;">
                    <img src="data:image/jpg;base64,{}" width="80">
                </div>
                <div style="text-align: center; font-size: 30px; font-weight: bold; margin-top: 10px; font-family: 'Open Sans', sans-serif;">
                    InternationAlly by PropertyPilot
                </div>
                <div style="text-align: center; font-size: 22px;">
                    Your Ally Abroad! 🚀
                </div>
            </div>
            """.format(load_image_as_base64("ally-logo.png")),  # Ensure the path is correct
            unsafe_allow_html=True
        )

        # Buttons positioned at the bottom
        with st.container():
            st.markdown('<div class="sidebar-buttons">', unsafe_allow_html=True)
            if st.button("Clear Conversation"):
                st.session_state.chat_histories[current_user] = [
                    {
                        "role": "assistant",
                        "content": f"Hello {first_name}! I know being an international student can feel like a lot, especially in a place like the U.S., where everything might feel new and different. How are you feeling about everything so far? Any specific areas where you’re feeling like you could use a bit of help or extra advice?"
                    }
                ]
                st.session_state.current_map_html = None  # Clear map when clearing chat
                st.success("Chat history cleared.")
                st.experimental_rerun()

            if st.button("Edit Profile"):
                st.session_state.editing_profile = True  # Toggle to profile editing mode
                st.experimental_rerun()

            if st.button("Log Out"):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.experimental_rerun()

            st.markdown('</div>', unsafe_allow_html=True)


    # Main chat UI

    # Display chat messages
    for message in st.session_state.chat_histories[current_user]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for user to type messages
    if user_input := st.chat_input("Enter your query here:"):
        st.session_state.chat_histories[current_user].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process the user input with the chatbot
        response, map_html, intent = chat_all(
            st.session_state.chat,
            st.session_state.prompts_dict,
            user_input,
            st.session_state.vectordb,
            st.session_state.user_onboarding_data[current_user]
        )

        # Display the chatbot's response
        with st.chat_message("assistant"):
            placeholder = st.empty()
            gradual_text = ""

            with st.spinner("Thinking..."):
                for word in response.split():
                    gradual_text += word + " "
                    placeholder.markdown(gradual_text)
                    time.sleep(0.05)

            # Finalize the placeholder with the complete response
            placeholder.markdown(response)

        # Add the response to chat history
        st.session_state.chat_histories[current_user].append({"role": "assistant", "content": response})

        # Update the map if needed
        if map_html and map_html != st.session_state.current_map_html:
            st.session_state.current_map_html = map_html
        else:
            st.session_state.current_map_html = None  # Set to None if no map is provided

    # Conditionally display the map only if there is content
    if st.session_state.get("current_map_html"):
        st.components.v1.html(st.session_state.current_map_html, height=500, width=710)  # Adjust height and width as needed

if not st.session_state.logged_in:
    if st.session_state.show_onboarding:
        onboarding_page()
    elif st.session_state.show_signup:
        signup_page()
    else:
        login_page()
else:
    chat_app()

