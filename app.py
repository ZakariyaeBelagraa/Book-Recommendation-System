import streamlit as st
import pandas as pd
import os
import re
import math
from recommander import book_indices,tfidf_matrix,knn,recommend_books_knn_with_fuzzy
from email_service import send_book_recommendations
from extract_text_from_image import extract_text_from_image


USER_DATA_FILE = "data/user_data.csv"
BOOKS_DATA_FILE = "data/books_data.csv"

if not os.path.exists(USER_DATA_FILE):
    pd.DataFrame(columns=["username", "email"]).to_csv(USER_DATA_FILE, index=False)

if not os.path.exists(BOOKS_DATA_FILE):
    pd.DataFrame(columns=["isbn13", "title", "image", "categories", "thumbnail","description", "liked_by"]).to_csv(BOOKS_DATA_FILE, index=False)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Email validation function
def is_valid_email(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None

st.header("Book Recommendation System")

st.sidebar.header("User Authentication")
if not st.session_state.logged_in:
    action = st.sidebar.radio("Select Action", ["Log In", "Create Profile"])

    if action == "Create Profile":
        st.sidebar.subheader("Create a New Profile")
        username = st.sidebar.text_input("Username (for profile creation)")
        email = st.sidebar.text_input("Email",help="This will be used to send you book recommendations. Make sure it's correct.")
        if st.sidebar.button("Create Profile"):
            user_data = pd.read_csv(USER_DATA_FILE)
            if username in user_data["username"].values:
                st.sidebar.error("Username already exists.")
            elif not is_valid_email(email):
                st.sidebar.error("Invalid email address. Please enter a valid email.")
            else:
                new_user = pd.DataFrame([{"username": username, "email": email}])
                user_data = pd.concat([user_data, new_user], ignore_index=True)
                user_data.to_csv(USER_DATA_FILE, index=False)
                st.sidebar.success("Profile created successfully!")
                st.session_state.logged_in = True
                st.session_state.current_user = new_user.iloc[0]
                st.session_state.username = username
                st.session_state.email = email
                st.rerun()

    elif action == "Log In":
        st.sidebar.subheader("Log In to Your Account")
        username = st.sidebar.text_input("Username (for login)")
        if st.sidebar.button("Log In"):
            user_data = pd.read_csv(USER_DATA_FILE)
            if username in user_data["username"].values:
                user_info = user_data[user_data["username"] == username].iloc[0]

                st.sidebar.success(f"Welcome back, {username}!")
                st.session_state.logged_in = True
                st.session_state.current_user = user_info
                st.session_state.username = user_info["username"]
                st.session_state.email = user_info["email"]
                st.rerun()
            else:
                st.sidebar.error("Username not found. Please create a profile first.")
else:
    st.sidebar.success(f"Logged in as {st.session_state.current_user['username']}")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.username = None
        st.session_state.email = None
        st.rerun()


if st.session_state.logged_in:
    username = st.session_state.current_user["username"]
    st.subheader(f"Welcome, {username}!")
    
    tab = st.selectbox("Select a Tab", ["Home", "Recommendations"])

    if tab == "Home":

        st.subheader("View and Like Books")
        books_data = pd.read_csv(BOOKS_DATA_FILE)

        BOOKS_PER_PAGE = 10

        total_pages = math.ceil(len(books_data) / BOOKS_PER_PAGE)

        if "current_page" not in st.session_state:
            st.session_state.current_page = 1

        selected_page = st.selectbox(
            "Select Page",
            options=list(range(1, total_pages + 1)),
            index=st.session_state.current_page - 1,
            key="page_selector",
        )

        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()

        start_index = (st.session_state.current_page - 1) * BOOKS_PER_PAGE
        end_index = start_index + BOOKS_PER_PAGE

        if len(books_data) > 0:
            for _, book in books_data.iloc[start_index:end_index].iterrows():
                with st.container():
                    book_title = book.get('title', 'Unknown Title')
                    book_subtitle = book.get('subtitle', 'No Subtitle')
                    book_authors = book.get('authors', 'Unknown Author')
                    book_categories = book.get('categories', 'Unknown Category')
                    published_year = book.get('published_year', 'N/A')
                    average_rating = book.get('average_rating', 'N/A')
                    num_pages = book.get('num_pages', 'N/A')
                    ratings_count = book.get('ratings_count', 'N/A')
                    
                    book_description = book.get('description', 'No description available.')
                    if not isinstance(book_description, str):
                        book_description = 'No description available.'
                    
                    truncated_description = (
                        book_description[:200] + "..." if len(book_description) > 200 else book_description
                    )
                    
                    if isinstance(book.get('thumbnail'), str) and book['thumbnail']:
                        thumbnail_html = f'<center><img src="{book["thumbnail"]}" alt="Book Thumbnail" style="width: 150px; border-radius: 10px;"/></center>'
                    else:
                        thumbnail_html = ""
                    
                    book_content = f"""
                    <div style="display: flex; border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Left side: Thumbnail -->
                        <div style="flex: 30%; text-align: center; padding-right: 20px;">
                            {thumbnail_html}
                        </div>
                        <!-- Right side: Book details -->
                        <div style="flex: 70%;">
                            <h4>{book_title}</h4>
                            <p><strong>Author(s):</strong> {book_authors}</p>
                            <p><strong>Categories:</strong> {book_categories}</p>
                            <p><strong>Published Year:</strong> {published_year}</p>
                            <p><strong>Average Rating:</strong> {average_rating} ({ratings_count} ratings)</p>
                            <p><strong>Number of Pages:</strong> {num_pages}</p>
                            <p>{truncated_description}</p>
                        </div>
                    </div>
                    """

                    st.markdown(book_content, unsafe_allow_html=True)

        else:
            st.write("No books available yet.")
            
        st.write(f"Page {st.session_state.current_page} of {total_pages}")



    
    if tab == "Recommendations":
        st.subheader("Search for Book Recommendations")
        
        input_method = st.radio("How would you like to search?", ["By Title", "By Image"])
        search_title = None
        
        if input_method == "By Title":
            search_title = st.text_input("Enter the title of a book:")
        elif input_method == "By Image":
            uploaded_file = st.file_uploader("Upload an image with text:", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                image_path = os.path.join("temp", uploaded_file.name)
                os.makedirs("temp", exist_ok=True)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                extracted_text = extract_text_from_image(image_path)

                if extracted_text:
                    search_title = extracted_text.strip()
                else:
                    st.warning("No text found in the image.")
                
                os.remove(image_path)
        
        if search_title:
            books_data = pd.read_csv(BOOKS_DATA_FILE)
            result = recommend_books_knn_with_fuzzy(search_title, knn, tfidf_matrix, book_indices, books_data)

            if len(result) == 2:
                closest_title, recommended_books_data = result

                if st.button("send Recommendations"):
                    book_titles = [book["title"] for book in recommended_books_data]
                    send_book_recommendations(st.session_state.email, st.session_state.username, closest_title, book_titles)
                    st.success(f"Email sent successfully to {st.session_state.email}")



                closest_book_data = books_data[books_data['title'] == closest_title].iloc[0]

                book_title = closest_book_data.get('title', 'Unknown Title')
                book_authors = closest_book_data.get('authors', 'Unknown Author')
                book_categories = closest_book_data.get('categories', 'Unknown Category')
                published_year = closest_book_data.get('published_year', 'N/A')
                average_rating = closest_book_data.get('average_rating', 'N/A')
                ratings_count = closest_book_data.get('ratings_count', 'N/A')
                num_pages = closest_book_data.get('num_pages', 'N/A')

                book_description = closest_book_data.get('description', 'No description available.')
                if not isinstance(book_description, str):
                    book_description = 'No description available.'

                truncated_description = (
                    book_description[:200] + " ..." if len(book_description) > 200 else book_description
                )

                thumbnail_url = closest_book_data.get('thumbnail', '')

                thumbnail_html = f'<img src="{thumbnail_url}" alt="{book_title}" style="max-width: 100%; height: auto; border-radius: 10px;">' if thumbnail_url else ""

                closest_book_content = f"""
                <div style="display: flex; border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
                    <div style="flex: 30%; text-align: center; padding-right: 20px;">
                        {thumbnail_html}
                    </div>
                    <div style="flex: 70%;">
                        <h4>{book_title}</h4>
                        <p><strong>Author(s):</strong> {book_authors}</p>
                        <p><strong>Categories:</strong> {book_categories}</p>
                        <p><strong>Published Year:</strong> {published_year}</p>
                        <p><strong>Average Rating:</strong> {average_rating} ({ratings_count} ratings)</p>
                        <p><strong>Number of Pages:</strong> {num_pages}</p>
                        <p>{truncated_description}</p>
                    </div>
                </div>
                """

                st.markdown(closest_book_content, unsafe_allow_html=True)



                st.subheader("Recommended Books:")

                for book_data in recommended_books_data:
                    book_title = book_data.get('title', 'Unknown Title')
                    book_authors = book_data.get('authors', 'Unknown Author')
                    book_categories = book_data.get('categories', 'Unknown Category')
                    published_year = book_data.get('published_year', 'N/A')
                    average_rating = book_data.get('average_rating', 'N/A')
                    ratings_count = book_data.get('ratings_count', 'N/A')
                    num_pages = book_data.get('num_pages', 'N/A')

                    book_description = book_data.get('description', 'No description available.')
                    if not isinstance(book_description, str):
                        book_description = 'No description available.'

                    truncated_description = (
                        book_description[:200] + " ..." if len(book_description) > 200 else book_description
                    )

                    thumbnail_url = book_data.get('thumbnail', '')

                    thumbnail_html = f'<img src="{thumbnail_url}" alt="{book_title}" style="max-width: 100%; height: auto; border-radius: 10px;">' if thumbnail_url else ""

                    book_content = f"""
                    <div style="display: flex; border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
                        <div style="flex: 30%; text-align: center; padding-right: 20px;">
                            {thumbnail_html}
                        </div>
                        <div style="flex: 70%;">
                            <h4>{book_title}</h4>
                            <p><strong>Author(s):</strong> {book_authors}</p>
                            <p><strong>Categories:</strong> {book_categories}</p>
                            <p><strong>Published Year:</strong> {published_year}</p>
                            <p><strong>Average Rating:</strong> {average_rating} ({ratings_count} ratings)</p>
                            <p><strong>Number of Pages:</strong> {num_pages}</p>
                            <p>{truncated_description}</p>
                        </div>
                    </div>
                    """

                    st.markdown(book_content, unsafe_allow_html=True)
            
            else:
                closest_title = result
                st.subheader(closest_title)


            

else:
    st.warning("Please log in to access the application.")
