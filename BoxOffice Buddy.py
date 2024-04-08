import sys
import os
import qrcode
import io
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QRadioButton, QGridLayout, QMessageBox, QScrollArea, QSpinBox, QCheckBox, QDialog, QGraphicsDropShadowEffect, QDateEdit, QFileDialog
)
from PyQt5.QtCore import QSize, Qt, QDate
from PyQt5.QtGui import QIcon, QImage, QPixmap, QColor

class ConfirmationDialog(QDialog):
    def __init__(self, movie, state, city, theater, showtime, selected_seats, num_popcorns, num_drinks, num_snacks_combo, total_price, selected_date, selected_language, selected_quality):
        super().__init__()
        self.setWindowTitle("BOB Ticket")  # Set the window title
        self.setWindowIcon(QIcon('D:\\Codes\\PPS Project OOPS\\Static\\img\\Colorful_Retro_Illustrative_Tasty_Popcorn_Logo2-removebg-preview.png'))
        # layout = QHBoxLayout()

        # IMDb URLs for each movie
        imdb_urls = {
            "Dune: Part 2 (UA)": "https://www.imdb.com/title/tt15239678/",
            "Shaitaan (A)": "https://www.imdb.com/title/tt27744786/",
            "Kung Fu Panda 4 (UA)": "https://www.imdb.com/title/tt21692408/",
            "Monkey Man (A)": "https://www.imdb.com/title/tt9214772/",
            "Maidaan (UA)": "https://www.imdb.com/title/tt10869778/",
            "Godzilla x Kong: The New Empire (UA)": "https://www.imdb.com/title/tt14539740/"
            # Add IMDb URLs for all movies you're displaying
        }

        # Modify the QR code data to include IMDb URL
        imdb_url = imdb_urls.get(movie.title, 'N/A')
        qr_data = imdb_url

        movie_qr_layout = QHBoxLayout()

        # Display selected movie poster with adjusted size and alignment
        movie_poster_label = QLabel()
        movie_poster_pixmap = QPixmap(movie.poster_path)
        movie_poster_label.setPixmap(movie_poster_pixmap.scaledToWidth(200))
        movie_poster_label.setAlignment(Qt.AlignCenter)  # Align the poster to the center
        movie_qr_layout.addWidget(movie_poster_label)
        # layout.addWidget(movie_poster_label)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        qr_code_image = QPixmap.fromImage(QImage.fromData(buffer.getvalue()))

        # Display QR code
        qr_code_label = QLabel()
        qr_code_label.setPixmap(qr_code_image)
        movie_qr_layout.addWidget(qr_code_label)

        # Create a layout to hold the movie details and QR code layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(movie_qr_layout)

        # Display selected movie details
        movie_details_label = QLabel(f"<b>Movie:</b> {movie.title}<br>"
                                     f"<b>Runtime:</b> {movie.runtime}<br>"
                                     f"<b>Rating:</b> {movie.rating}<br>"
                                     f"<b>Genre:</b> {movie.genre}<br>"
                                     f"<b>Description:</b> {movie.description}<br>"
                                     f"<b>Language:</b> {selected_language}<br>"
                                     f"<b>Quality:</b> {selected_quality}<br>")
        main_layout.addWidget(movie_details_label)

        # Display selected location and showtime
        location_label = QLabel(f"<b>Location:</b> {state}, {city}<br>"
                                f"<b>Theater:</b> {theater}<br>"
                                f"<b>Showtime:</b> {showtime}<br>"
                                f"<b>Date:</b> {selected_date.day()}-{selected_date.month()}-{selected_date.year()}<br>")
        main_layout.addWidget(location_label)

        # Display selected seats
        seats_label = QLabel(f"<b>Selected Seats:</b> {', '.join(selected_seats)}<br>")
        main_layout.addWidget(seats_label)

        # Display if snacks are selected
        snacks_label = QLabel(f"<b>Snacks:</b> {'Yes' if num_popcorns + num_drinks + num_snacks_combo > 0 else 'No'}<br>"
                              f"<b>Popcorns:</b> {num_popcorns}<br>"
                              f"<b>Drinks:</b> {num_drinks}<br>"
                              f"<b>Snacks Combo:</b> {num_snacks_combo}<br>")
        main_layout.addWidget(snacks_label)

        # Calculate total price including 18% GST
        total_with_gst = total_price * 1.18
        total_label = QLabel(f"<b>Total Price (including 18% GST):</b> ₹{total_price:.2f}<br>")
        main_layout.addWidget(total_label)

        # Add a button to download ticket as an image
        download_button = QPushButton("Download Ticket")
        download_button.clicked.connect(self.save_ticket_as_image)
        main_layout.addWidget(download_button)

        self.setLayout(main_layout)

    def save_ticket_as_image(self):
        default_file_name = "BoxOffice Buddy Ticket.png"
        filename, _ = QFileDialog.getSaveFileName(self, "Save Ticket", default_file_name, "PNG Files (*.png)")
        if filename:
            pixmap = self.grab()
            pixmap.save(filename, "PNG")
            QMessageBox.information(self, "Ticket Saved", "Ticket saved successfully!")

class Movie:
    def __init__(self, title, poster_path, runtime, rating, genre, description, languages=None, qualities=None):
        self.title = title
        self.poster_path = poster_path
        self.runtime = runtime
        self.rating = rating
        self.genre = genre
        self.description = description
        self.languages = languages or []  # Default to an empty list if languages are not provided
        self.qualities = qualities or []

    def calculate_price(self, diamond_seats, gold_seats, silver_seats, popcorns, drinks, snacks_combo):
        diamond_price = 350 * diamond_seats
        gold_price = 250 * gold_seats
        silver_price = 150 * silver_seats
        popcorn_price = popcorns  # Price is already calculated based on quantity
        drinks_price = drinks  # Price is already calculated based on quantity
        snacks_combo_price = snacks_combo  # Price is already calculated based on quantity

        total_price = diamond_price + gold_price + silver_price + popcorn_price + drinks_price + snacks_combo_price
        return total_price

class MovieBookingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.movie_buttons = []
        self.movie_posters = []  # Initialize movie_posters as an empty list
        self.movie_poster_infos = []  # Initialize movie_poster_infos as an empty list
        self.setWindowTitle('BoxOffice Buddy')
        self.setWindowIcon(QIcon('D:\\Codes\\PPS Project OOPS\\Static\\img\\Colorful_Retro_Illustrative_Tasty_Popcorn_Logo2-removebg-preview.png'))
        self.setGeometry(100, 100, 800, 600)
        self.showFullScreen()
        self.theaters = {
            'PVR': {
                'Dune: Part 2 (UA)': ['10:00 AM', '1:00 PM', '4:00 PM', '7:00 PM'],
                'Shaitaan (A)': ['11:00 AM', '2:00 PM', '5:00 PM', '9:00 PM'],
                'Kung Fu Panda 4 (UA)': ['10:30 AM', '12:00 PM', '4:30 PM', '8:00 PM'],
                'Monkey Man (A)': ['9:00 AM', '3:00 PM', '8:30 PM', '10:00 PM'],
                'Maidaan (UA)': ['9:30 AM', '3:30 PM', '8:40 PM', '11:00 PM'],
                'Godzilla x Kong: The New Empire (UA)': ['9:00 AM', '3:00 PM', '8:30 PM', '10:00 PM']
            },
            'Inox': {
                'Dune: Part 2 (UA)': ['11:00 AM', '2:00 PM', '5:00 PM', '9:00 PM'],
                'Shaitaan (A)': ['12:00 PM', '3:00 PM', '6:00 PM', '10:00 PM'],
                'Kung Fu Panda 4 (UA)': ['10:00 AM', '1:00 PM', '4:00 PM', '7:00 PM'],
                'Monkey Man (A)': ['9:30 AM', '2:30 PM', '7:30 PM', '9:30 PM'],
                'Maidaan (UA)': ['9:30 AM', '2:30 PM', '7:30 PM', '9:30 PM'],
                'Godzilla x Kong: The New Empire (UA)': ['9:30 AM', '2:30 PM', '7:30 PM', '9:30 PM']
            },
            'Cinepolis': {
                'Dune: Part 2 (UA)': ['10:00 AM', '1:00 PM', '4:00 PM', '7:00 PM'],
                'Shaitaan (A)': ['11:00 AM', '2:00 PM', '5:00 PM', '9:00 PM'],
                'Kung Fu Panda 4 (UA)': ['10:30 AM', '12:00 PM', '4:30 PM', '8:00 PM'],
                'Monkey Man (A)': ['9:00 AM', '3:30 PM', '8:30 PM', '10:00 PM'],
                'Maidaan (UA)': ['9:00 AM', '3:00 PM', '8:30 PM', '10:00 PM'],
                'Godzilla x Kong: The New Empire (UA)': ['9:00 AM', '2:00 PM', '8:30 PM', '10:00 PM']
            },
            'Delite Cinemas': {
                'Dune: Part 2 (UA)': ['11:00 AM', '2:00 PM', '5:00 PM', '9:00 PM'],
                'Shaitaan (A)': ['12:00 PM', '3:00 PM', '6:00 PM', '10:00 PM'],
                'Kung Fu Panda 4 (UA)': ['10:00 AM', '2:45 PM', '4:15 PM', '7:00 PM'],
                'Monkey Man (A)': ['9:45 AM', '2:30 PM', '7:30 PM', '9:30 PM'],
                'Maidaan (UA)': ['9:30 AM', '2:30 PM', '7:30 PM', '9:30 PM'],
                'Godzilla x Kong: The New Empire (UA)': ['8:30 AM', '2:30 PM', '7:30 PM', '9:30 PM']
            },
            'Miraj Cinemas': {  # Add Miraj Cinemas theater
                'Dune: Part 2 (UA)': ['10:00 AM', '1:00 PM', '4:00 PM', '7:00 PM'],
                'Shaitaan (A)': ['11:00 AM', '2:00 PM', '5:00 PM', '9:00 PM'],
                'Kung Fu Panda 4 (UA)': ['10:30 AM', '12:00 PM', '4:30 PM', '8:00 PM'],
                'Monkey Man (A)': ['10:30 AM', '3:00 PM', '8:30 PM', '10:00 PM'],
                'Maidaan (UA)': ['9:00 AM', '3:00 PM', '8:30 PM', '10:00 PM'],
                'Godzilla x Kong: The New Empire (UA)': ['9:45 AM', '3:00 PM', '8:30 PM', '10:00 PM']
            }
        }

        self.create_layout()
        self.populate_state_city_combo()
        self.populate_movie_combo()
        self.displayMovieDetails()
        self.populate_language_quality_combo()
        self.populate_theater_showtime_combo()
        self.movie_Hlayout = None
        self.movie_Vlayout = None

    def create_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        title_label = QLabel("Welcome to BoxOffice Buddy", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        central_widget.setStyleSheet("background-color: bright red;")

        layout.addWidget(self.create_state_city_group())
        layout.addWidget(self.create_movie_group())
        layout.addWidget(self.create_language_quality_group())
        layout.addWidget(self.create_theater_showtime_group())
        layout.addWidget(self.create_seat_group())
        layout.addWidget(self.create_snack_group())
        layout.addWidget(self.create_button_group())

        central_widget.setLayout(layout)

    def create_state_city_group(self):
        group_box = QGroupBox('Select State and City')
        layout = QVBoxLayout()

        self.state_combobox = QComboBox()
        layout.addWidget(self.state_combobox)

        self.city_combobox = QComboBox()
        layout.addWidget(self.city_combobox)

        group_box.setLayout(layout)
        return group_box

    def create_movie_group(self):
        group_box = QGroupBox('Select Movie')
        self.movie_Hlayout = QHBoxLayout();
        group_box.setLayout(self.movie_Hlayout)
        return group_box
    
    def create_language_quality_group(self):
        group_box = QGroupBox('Select Language and Quality')  # Create a group box
        layout = QVBoxLayout()

        self.language_combobox = QComboBox()  # Create a language combo box
        layout.addWidget(self.language_combobox)

        self.quality_combobox = QComboBox()  # Create a quality combo box
        layout.addWidget(self.quality_combobox)

        group_box.setLayout(layout)
        return group_box
    
    def populate_language_quality_combo(self):
        self.language_combobox.currentTextChanged.connect(self.update_quality_combo)
        self.quality_combobox.currentTextChanged.connect(self.update_theater_showtime_combo)
        self.initialize_language_quality_combo()

    def initialize_language_quality_combo(self):
        self.language_combobox.clear()
        self.quality_combobox.clear()
        self.language_combobox.addItem('Select Language')
        self.quality_combobox.addItem('Select Quality')

    def create_theater_showtime_group(self):
        group_box = QGroupBox('Select Theater, Select Date and Showtime')
        layout = QVBoxLayout()

        self.theater_combobox = QComboBox()
        self.showtime_combobox = QComboBox()

        layout.addWidget(self.theater_combobox)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)  # Enable calendar popup for easy date selection
        self.date_edit.setDate(QDate.currentDate())  # Set default date to current date
        layout.addWidget(self.date_edit)

        self.date_edit.dateChanged.connect(self.update_showtime_combo)

        layout.addWidget(self.showtime_combobox)

        group_box.setLayout(layout)

    # Connect the update_showtime_combo method to the currentTextChanged signal of the theater combobox
        self.theater_combobox.currentTextChanged.connect(self.update_showtime_combo)

        return group_box  # Add this return statement to return the group_box

    def create_seat_group(self):
        group_box = QGroupBox('Select Seats')   
        layout = QVBoxLayout()

    # Diamond Seats
        diamond_label = QLabel("Diamond - (₹350)")
        layout.addWidget(diamond_label)
        self.diamond_seat_grid = QGridLayout()
        self.populate_diamond_seat_grid()
        layout.addLayout(self.diamond_seat_grid)

    # Gold Seats
        gold_label = QLabel("Gold - ₹250")
        layout.addWidget(gold_label)
        self.gold_seat_grid = QGridLayout()
        self.populate_gold_seat_grid()
        layout.addLayout(self.gold_seat_grid)

    # Silver Seats
        silver_label = QLabel("Silver - ₹150")
        layout.addWidget(silver_label)
        self.silver_seat_grid = QGridLayout()
        self.populate_silver_seat_grid()
        layout.addLayout(self.silver_seat_grid)

    # Create a scroll area
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_content.setLayout(layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)

        group_box.setLayout(QVBoxLayout())
        group_box.layout().addWidget(scroll_area)
        return group_box

    def populate_diamond_seat_grid(self):
        num_rows = 3
        num_cols = 20
        for row in range(num_rows):
            for col in range(num_cols):
                seat_button = QPushButton(f'D{row + 1},{col + 1}')
                seat_button.setCheckable(True)
                seat_button.setStyleSheet('''
                    QPushButton {
                        width: 30px;
                        height: 30px;
                        border: none;
                        border-radius: 5px;
                        background-color: white;
                    }
                    QPushButton:checked {
                        background-color: coral;
                    }
                ''')
                self.diamond_seat_grid.addWidget(seat_button, row, col)

    def populate_gold_seat_grid(self):
        num_rows = 5
        num_cols = 20
        for row in range(num_rows):
            for col in range(num_cols):
                seat_button = QPushButton(f'G{row + 1},{col + 1}')
                seat_button.setCheckable(True)
                seat_button.setStyleSheet('''
                    QPushButton {
                        width: 30px;
                        height: 30px;
                        border: none;
                        border-radius: 5px;
                        background-color: white;
                    }
                    QPushButton:checked {
                        background-color: coral;
                    }
                ''')
                self.gold_seat_grid.addWidget(seat_button, row, col)

    def populate_silver_seat_grid(self):
        num_rows = 4
        num_cols = 20
        for row in range(num_rows):
            for col in range(num_cols):
                seat_button = QPushButton(f'S{row + 1},{col + 1}')
                seat_button.setCheckable(True)
                seat_button.setStyleSheet('''
                    QPushButton {
                        width: 30px;
                        height: 30px;
                        border: none;
                        border-radius: 5px;
                        background-color: white;
                    }
                    QPushButton:checked {
                        background-color: coral;
                    }
                ''')
                self.silver_seat_grid.addWidget(seat_button, row, col)


    def create_snack_group(self):
        group_box = QGroupBox('Preorder Snacks')
        layout = QVBoxLayout()

    # Popcorn Slider
        popcorn_layout = QHBoxLayout()
        self.popcorn_slider = QSpinBox()
        self.popcorn_slider.setRange(0, 10)  # Set the range as per requirement
        self.popcorn_slider.setValue(0)  # Set the default value
        popcorn_label = QLabel('Popcorn (₹250)')
        popcorn_layout.addWidget(popcorn_label)
        popcorn_layout.addWidget(self.popcorn_slider)
        layout.addLayout(popcorn_layout)

    # Drinks Slider
        drinks_layout = QHBoxLayout()
        self.drinks_slider = QSpinBox()
        self.drinks_slider.setRange(0, 10)  # Set the range as per requirement
        self.drinks_slider.setValue(0)  # Set the default value
        drinks_label = QLabel('Drinks (₹250)')
        drinks_layout.addWidget(drinks_label)
        drinks_layout.addWidget(self.drinks_slider)
        layout.addLayout(drinks_layout)

    # Snacks Combo Slider
        snacks_combo_layout = QHBoxLayout()
        self.snacks_combo_slider = QSpinBox()
        self.snacks_combo_slider.setRange(0, 10)  # Set the range as per requirement
        self.snacks_combo_slider.setValue(0)  # Set the default value
        snacks_combo_label = QLabel('Snacks Combo (₹500)')
        snacks_combo_layout.addWidget(snacks_combo_label)
        snacks_combo_layout.addWidget(self.snacks_combo_slider)
        layout.addLayout(snacks_combo_layout)

        group_box.setLayout(layout)
        return group_box

    def create_button_group(self):
        group_box = QGroupBox('')
        layout = QVBoxLayout()

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.back_button_clicked)
        layout.addWidget(back_button)

        book_button = QPushButton('Book')
        book_button.clicked.connect(self.book_button_clicked)
        layout.addWidget(book_button)

        group_box.setLayout(layout)
        return group_box

    def populate_state_city_combo(self):
        states = ['Andhra Pradesh', 'Bihar', 'Gujarat', 'Karnataka', 'Madhya Pradesh', 'Maharashtra', 'Odisha', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal']
        self.state_combobox.addItems(['Select State'] + states)
        self.state_combobox.currentTextChanged.connect(self.populate_city_combo)
        if self.state_combobox.count() > 1:
            self.state_combobox.setCurrentIndex(0)
            self.populate_city_combo(None)

    def populate_city_combo(self, state):
        cities = {
            'Andhra Pradesh': ['Hyderabad', 'Vishakapatnam', 'Vijayawada'],
            'Bihar': ['Patna', 'Gaya', 'Muzaffarpur'],
            'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara'],
            'Karnataka': ['Bangalore', 'Mysore', 'Hubli'],
            'Madhya Pradesh': ['Indore', 'Bhopal', 'Jabalpur'],
            'Maharashtra': ['Mumbai', 'Pune', 'Nagpur'],
            'Odisha': ['Bhubaneswar', 'Cuttack', 'Puri'],
            'Punjab': ['Chandigarh', 'Ludhiana', 'Amritsar'],
            'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur'],
            'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai'],
            'Uttar Pradesh': ['Varanasi','Lucknow', 'Kanpur', 'Agra'],
            'West Bengal': ['Kolkata', 'Siliguri', 'Durgapur']
        }
        if state is None:
            state = self.state_combobox.currentText()
        self.city_combobox.clear()
        self.city_combobox.addItems(['Select City'] + cities.get(state, []))
        self.update_showtime_combo()

    def populate_movie_combo(self):
        img_path = 'D:\\Codes\\PPS Project OOPS\\Static\\img\\';
        self.movies = [
            ('Dune: Part 2 (UA)', img_path+'1.jpg', '2H 46M', 8.8, 'Action, Adventure, Sci-Fi', 'Paul seeks revenge, fates challenge.', ['English', 'Hindi'], ['2D', '3D', 'IMAX 2D', 'IMAX 3D', 'ICE 2D', 'ICE 3D', 'MX4D', '4DX', '2D SCREEN X', '3D SCREEN X']),
            ('Shaitaan (A)', img_path+'3.jpg', '2H 12M', 7.8, 'Supernatural, Thriller', 'Family weekend turns terrifying.', ['Hindi'], ['2D', 'ICE 2D']),
            ('Kung Fu Panda 4 (UA)', img_path+'2.jpg', '1H 33M', 6.5, 'Action, Adventure, Animation, Comedy', 'Po faces new villain in city.', ['English', 'Hindi', 'Tamil', 'Telugu'], ['2D', '3D', '3D SCREEN X', '4DX', 'ICE 2D', 'ICE 3D', 'MX4D 3D', '4DX 3D', '2D SCREEN X']),
            ('Monkey Man (A)', img_path+'5.jpg', '1H 53M', 8.5, 'Action, Adventure', 'Rookie avenges mother death.', ['Hindi', 'English', 'Tamil', 'Telugu'], ['2D']),
            ('Maidaan (UA)', img_path+'6.jpg', '3H 1M', 7.5, 'Biography, Drama, Sports', 'A Man pursuit of national glory.', ['Hindi'], ['2D', 'IMAX 2D']),
            ('Godzilla x Kong: The New Empire (UA)', img_path+'4.jpg', '1H 54M', 6.6 , 'Action, Sci-Fi,Thriller', 'Kong & Godzilla confront ominous hidden foe.', ['English', 'Hindi', 'Tamil', 'Telugu'], ['2D', 'MX4D 3D', '3D', 'IMAX 2D', 'IMAX 3D', '4DX', '4DX 3D', 'ICE 3D', 'SCREEN X', '3D SCREEN X']),
            # Add more movies here
        ]
        self.language_combobox.clear()
        self.quality_combobox.clear()
        for movie in self.movies:
        # Check if the movie tuple has enough elements
            if len(movie) >= 8:
                languages = movie[6]
                if languages:
                    self.language_combobox.addItems(languages)
                qualities = movie[7]
                if qualities:
                    self.quality_combobox.addItems(qualities)
            else:
                print(f"Warning: Incomplete movie information: {movie}")

    def update_theater_showtime_combo(self):
        selected_movie = self.get_selected_movie()
        selected_language = self.language_combobox.currentText()
        selected_quality = self.quality_combobox.currentText()

        if selected_movie and selected_language and selected_quality:
            theaters = self.theaters.keys()
            self.theater_combobox.clear()
            self.theater_combobox.addItem('Select Theater')
            self.theater_combobox.addItems(theaters)

    def displayMovieDetails(self):
        for movie in self.movies:
            layout = QVBoxLayout()  
            movie_button = QPushButton()
            movie_button.setIcon(QIcon(movie[1]))  
            movie_button.setIconSize(QSize(100, 150))  
            movie_button.setFixedSize(QSize(110, 160))  

            # Add shadow effect to the movie poster button
            shadow_effect = QGraphicsDropShadowEffect()
            shadow_effect.setBlurRadius(10)
            shadow_effect.setColor(QColor(0, 0, 0, 150))
            shadow_effect.setOffset(5, 5)
            movie_button.setGraphicsEffect(shadow_effect)

            movie_button.setStyleSheet(
                '''
                QPushButton {
                    border: 2px solid #007bff;  
                    border-radius: 0px; /* Set border-radius to 0 for rectangle */
                    background-color: white;  
                }
                QPushButton:checked {
                    border: 2px solid red;  /* Change color to red when selected */
                    background-color: yellow;  /* Change background color when selected */
                }
                '''
            )
            movie_button.setCheckable(True)
            movie_button.clicked.connect(lambda state, movie=movie: self.select_movie(movie))
            layout.addWidget(movie_button)
            self.movie_buttons.append(movie_button)  

            movie_info_label = QLabel()
            movie_info_label.setText(f'<b>{movie[0]}</b><br>'
                            f'Runtime: {movie[2]}<br>'
                            f'Rating: {movie[3]}<br>'
                            f'Genre: {movie[4]}<br>'
                            f'Description: {movie[5]}<br>')
            layout.addWidget(movie_info_label)

            play_trailer_button = QPushButton("Play Trailer")
            play_trailer_button.setFixedWidth(100)
            play_trailer_button.clicked.connect(lambda state, movie=movie: self.play_trailer(movie[0]))
            layout.addWidget(play_trailer_button)

            self.movie_Hlayout.addLayout(layout)  
            self.movie_posters.append(movie_button)  
            self.movie_poster_infos.append(movie_info_label)

    def play_trailer(self, movie_title):
        trailer_urls = {
            'Dune: Part 2 (UA)': 'https://youtu.be/Way9Dexny3w?si=hWDtykJpK6Xg8p5N',
            'Shaitaan (A)': 'https://youtu.be/Yxe-mIVIwM4?si=39QLo5wX3HGp3NpN',
            'Kung Fu Panda 4 (UA)': 'https://youtu.be/_inKs4eeHiI?si=b8CP8ouvLoyfFCs5',
            'Monkey Man (A)': 'https://youtu.be/g8zxiB5Qhsc?si=HCkRObKyYoEsmt6U',
            'Maidaan (UA)': 'https://youtu.be/bJI0Kj0OgNo?si=CJr8X8JseNu23x9O',
            'Godzilla x Kong: The New Empire (UA)': 'https://youtu.be/lV1OOlGwExM?si=diLT_LUVyXTU24ja'
        }

        # Get the trailer URL for the selected movie title
        trailer_url = trailer_urls.get(movie_title)

        if trailer_url:
            webbrowser.open(trailer_url)
        else:
            QMessageBox.warning(self, "Trailer Not Found", "Trailer not available for this movie.")

    def select_movie(self, movie):
        index = self.movies.index(movie)
        if 0 <= index < len(self.movie_buttons):  # Check if index is within the range of movie_buttons
            for idx in range(len(self.movie_buttons)):
                if(idx != index):
                    self.movie_buttons[idx].setChecked(False);                
                self.movie_buttons[idx].setStyleSheet("border: none; background-color: none;")
            self.movie_buttons[index].setStyleSheet("border: 2px solid red; background-color: yellow;")
            self.language_combobox.clear()
            self.quality_combobox.clear()
            self.language_combobox.addItem('Select Language')
            self.quality_combobox.addItem('Select Quality')
            self.language_combobox.addItems(movie[6])  # Add languages
            self.quality_combobox.addItems(movie[7])  # Add qualities
        else:
            print("Index out of range:", index)

    def handle_theater_changed(self, str):
        self.showtime_combobox.clear();
        self.showtime_combobox.addItem('Select Showtime');

        selected_theater = self.theater_combobox.currentText(); 

        if selected_theater and selected_theater != 'Select Theater':
            theater_timings = list(self.theaters[selected_theater]);                  
            self.showtime_combobox.addItems(theater_timings);

    def populate_theater_showtime_combo(self):
        self.theater_combobox.currentTextChanged.connect(self.update_showtime_combo)
        self.initialize_theater_combo()

    def initialize_theater_combo(self):
        theaters = list(self.theaters.keys())
        self.theater_combobox.clear()
        self.showtime_combobox.clear()

        self.theater_combobox.addItem('Select Theater')
        self.theater_combobox.addItems(theaters)
        self.showtime_combobox.addItem('Select Showtime')

    def update_showtime_combo(self):
        selected_theater = self.theater_combobox.currentText()
        # print(selected_theater)
        selected_date = self.date_edit.date().toString(Qt.ISODate)

        if selected_theater in self.theaters:
            theater_movie_and_times = self.theaters[selected_theater];
            selected_movie = self.get_selected_movie();
            theater_showtimes = theater_movie_and_times[selected_movie.title] if selected_movie != None else [];
            self.showtime_combobox.clear()
            self.showtime_combobox.addItem('Select Showtime')
            self.showtime_combobox.addItems(theater_showtimes)  # Add showtimes to the combo box

    def update_quality_combo(self):
        selected_movie = self.get_selected_movie()
        if selected_movie:
            self.quality_combobox.clear()
            self.quality_combobox.addItem('Select Quality')
            self.quality_combobox.addItems(selected_movie.qualities)

    def get_selected_movie(self):
        for button, movie_info in zip(self.movie_buttons, self.movies):
            if button.isChecked():
                title, poster_path, runtime, rating, genre, description, languages, qualities = movie_info
                return Movie(title, poster_path, runtime, rating, genre, description, languages, qualities)
        return None

    def populate_seat_grid(self):
        num_rows = 10
        num_cols = 20
        for row in range(num_rows):
            for col in range(num_cols):
                seat_button = QPushButton(f'{row + 1},{col + 1}')
                seat_button.setCheckable(True)
                seat_button.setStyleSheet('''
                    QPushButton {
                        width: 30px;
                        height: 30px;
                        border: none;
                        border-radius: 5px;
                        background-color: white;
                    }
                    QPushButton:checked {
                        background-color: coral;
                    }
                ''')
                self.seat_grid.addWidget(seat_button, row, col)

    def get_selected_seat_count(self, seat_type):
        count = 0
        if seat_type == 'diamond':
            for row in range(3):
                for col in range(20):
                    button = self.diamond_seat_grid.itemAtPosition(row, col).widget()
                    if button.isChecked():
                        count += 1
        elif seat_type == 'gold':
            for row in range(5):
                for col in range(20):
                    button = self.gold_seat_grid.itemAtPosition(row, col).widget()
                    if button.isChecked():
                        count += 1
        elif seat_type == 'silver':
            for row in range(4):
                for col in range(20):
                    button = self.silver_seat_grid.itemAtPosition(row, col).widget()
                    if button.isChecked():
                        count += 1
        return count

    def back_button_clicked(self):
        self.state_combobox.setCurrentIndex(0)
        self.city_combobox.setCurrentIndex(0)
        self.movie_combobox.setCurrentIndex(0)
        self.theater_combobox.setCurrentIndex(0)
        self.showtime_combobox.setCurrentIndex(0)
        self.populate_seat_grid()

        self.popcorn_checkbox.setChecked(False)
        self.drinks_checkbox.setChecked(False)
        self.snacks_checkbox.setChecked(False)

    def book_button_clicked(self):
        selected_theater = self.theater_combobox.currentText()
        selected_showtime = self.showtime_combobox.currentText()
        selected_date = self.date_edit.date()  # Get the selected date
        selected_language = self.language_combobox.currentText()
        selected_quality = self.quality_combobox.currentText()

        if not selected_theater or not selected_showtime:
            QMessageBox.warning(self, 'Warning', 'Please select theater and showtime.')
            return

        # Calculate total price
        selected_movie = self.get_selected_movie()
        if selected_movie:
            subtotal_price = selected_movie.calculate_price(
                self.get_selected_seat_count('diamond'),
                self.get_selected_seat_count('gold'),
                self.get_selected_seat_count('silver'),
                self.popcorn_slider.value() * 250,  # Calculate popcorn price based on quantity
                self.drinks_slider.value() * 250,  # Calculate drinks price based on quantity
                self.snacks_combo_slider.value() * 500  # Calculate snacks combo price based on quantity
            )

            # Calculate total price including 18% GST
            total_price = subtotal_price * 1.18

            # Redirect to PayPal payment gateway
            self.redirect_to_paypal(total_price)

            num_popcorns = self.popcorn_slider.value()
            num_drinks = self.drinks_slider.value()
            num_snacks_combo = self.snacks_combo_slider.value()

    def redirect_to_paypal(self, total_price):
        payment_url = f'https://www.paypal.com?amount={total_price}&currency=INR'  # Assuming currency is INR
        webbrowser.open(payment_url)
        QMessageBox.information(self, 'Booking Confirmation', 'Your ticket has been booked successfully!')
        selected_movie = self.get_selected_movie()
        selected_state = self.state_combobox.currentText()
        selected_city = self.city_combobox.currentText()
        selected_theater = self.theater_combobox.currentText()
        selected_showtime = self.showtime_combobox.currentText()
        selected_date = self.date_edit.date()
        selected_language = self.language_combobox.currentText()
        selected_quality = self.quality_combobox.currentText()
        selected_seats = []
        for row in range(3):
            for col in range(20):
                button = self.diamond_seat_grid.itemAtPosition(row, col).widget()
                if button.isChecked():
                    selected_seats.append(f"D{row + 1},{col + 1}")
        for row in range(5):
            for col in range(20):
                button = self.gold_seat_grid.itemAtPosition(row, col).widget()
                if button.isChecked():
                    selected_seats.append(f"G{row + 1},{col + 1}")
        for row in range(4):
            for col in range(20):
                button = self.silver_seat_grid.itemAtPosition(row, col).widget()
                if button.isChecked():
                    selected_seats.append(f"S{row + 1},{col + 1}")

        num_popcorns = self.popcorn_slider.value()
        num_drinks = self.drinks_slider.value()
        num_snacks_combo = self.snacks_combo_slider.value()

        selected_snacks = any([num_popcorns, num_drinks, num_snacks_combo])
        
        dialog = ConfirmationDialog(selected_movie, selected_state, selected_city, selected_theater,
                                selected_showtime, selected_seats, num_popcorns, num_drinks, num_snacks_combo, total_price, selected_date, selected_language, selected_quality)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MovieBookingApp()
    window.show()
    sys.exit(app.exec_())
