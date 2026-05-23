
import customtkinter as ctk
import pandas as pd
from datetime import datetime
import os
import requests
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import filedialog
import tkinter.font as tkFont
import shutil

# Set appearance
ctk.set_appearance_mode("dark")


_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_FONT_PATH = os.path.join(_APP_DIR, "Audiowide-Regular.ttf")
AUDIOWIDE_LOADED = False

def _load_audiowide(root):
    global AUDIOWIDE_LOADED
    if os.path.exists(_FONT_PATH):
        try:
            root.tk.call("font", "create", "Audiowide")
            from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
            FR_PRIVATE  = 0x10
            FR_NOT_ENUM = 0x20
            try:
                windll.gdi32.AddFontResourceExW(_FONT_PATH, FR_PRIVATE, 0)
            except Exception:
                pass
            AUDIOWIDE_LOADED = True
        except Exception:
            AUDIOWIDE_LOADED = False

def audiowide_font(size, weight="normal"):
    """Return CTkFont using Audiowide if available, else bold fallback."""
    if AUDIOWIDE_LOADED:
        return ctk.CTkFont(family="Audiowide", size=size, weight=weight)
    # Fallback — looks close enough
    return ctk.CTkFont(family="Arial Black", size=size, weight=weight)

#  LAST.FM API CONFIGURATION 
LASTFM_API_KEY = "Your_Last.fm_API_Key_Here"  # Replace with your actual API key
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"

class AvanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load Audiowide font
        _load_audiowide(self)

        # App icon
        _icon_path = os.path.join(_APP_DIR, "icon.png")
        if os.path.exists(_icon_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(_icon_path)
                img = img.resize((64, 64), Image.LANCZOS)
                self._icon_img = ImageTk.PhotoImage(img)
                self.iconphoto(True, self._icon_img)
            except Exception:
                pass

        # Accessibility state
        self.font_size = 14   # base body font size

        # Window setup
        self.title("AVANCE - Fitness + Music")
        self.geometry("1200x800")
        self.configure(fg_color="#0f1117")

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.create_sidebar()

        # Create main area
        self.main_frame = ctk.CTkFrame(self, fg_color="#0f1117")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Show Log Workout by default
        self.show_page("Log Workout")

    def fs(self, base=13):
        """Scale a font size relative to accessibility setting."""
        return int(base + (self.font_size - 14))
        
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#13151f")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        
        self.sidebar_logo = ctk.CTkLabel(
            self.sidebar, text="AVANCE",
            font=audiowide_font(22),
            text_color="#4dd9c0"
        )
        self.sidebar_logo.grid(row=0, column=0, padx=20, pady=(35, 2), sticky="w")

        self.sidebar_subtitle = ctk.CTkLabel(
            self.sidebar, text="FITNESS . WORKOUT",
            font=ctk.CTkFont(size=9), text_color="#555"
        )
        self.sidebar_subtitle.grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        # Divider under logo
        top_div = ctk.CTkFrame(self.sidebar, fg_color="#2a2d3a", height=1)
        top_div.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))

        
        nav_items = [
            ("＋", "Log Workout"),
            ("⊞",  "Dashboard"),
            ("↗",  "Insights"),
            ("▦",  "History"),
        ]

        self.nav_buttons = {}

        for i, (icon, page_key) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {page_key}",
                command=lambda pk=page_key: self.show_page(pk),
                fg_color="transparent",
                text_color="#7a7f9a",
                hover_color="#1e2130",
                anchor="w",
                height=46,
                corner_radius=8,
                font=ctk.CTkFont(size=self.font_size)
            )
            btn.grid(row=i + 3, column=0, padx=12, pady=3, sticky="ew")
            self.nav_buttons[page_key] = btn

        # ── Spacer pushes settings to bottom ──────────
        self.sidebar.grid_rowconfigure(8, weight=1)

        # Divider above settings
        bot_div = ctk.CTkFrame(self.sidebar, fg_color="#2a2d3a", height=1)
        bot_div.grid(row=9, column=0, sticky="ew", padx=20, pady=(8, 4))

        # Settings button
        settings_btn = ctk.CTkButton(
            self.sidebar,
            text="  ⚙   Settings",
            command=lambda: self.show_page("Settings"),
            fg_color="transparent",
            text_color="#7a7f9a",
            hover_color="#1e2130",
            anchor="w",
            height=46,
            corner_radius=8,
            font=ctk.CTkFont(size=self.font_size)
        )
        settings_btn.grid(row=10, column=0, padx=12, pady=(0, 24), sticky="ew")
        self.nav_buttons["Settings"] = settings_btn

    def refresh_sidebar_fonts(self):
        """Update sidebar button fonts after font size change"""
        for btn in self.nav_buttons.values():
            btn.configure(font=ctk.CTkFont(size=self.font_size))

    def set_active_nav(self, page_key):
        """Highlight the active nav item"""
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(fg_color="#1e2a35", text_color="#4dd9c0")
            else:
                btn.configure(fg_color="transparent", text_color="#7a7f9a")
    
    def clear_main_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_page(self, page_name):
        self.clear_main_frame()
        self.set_active_nav(page_name)
        if page_name != "Settings":
            self._last_page = page_name
        if page_name == "Log Workout":
            self.show_log_workout()
        elif page_name == "Dashboard":
            self.show_dashboard()
        elif page_name == "Insights":
            self.show_insights()
        elif page_name == "History":
            self.show_history()
        elif page_name == "Settings":
            self.show_settings()
    
    
    def show_log_workout(self):
        """Log Workout page — labels above fields, clear errors, template card"""
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="#0f1117",
            scrollbar_button_color="#2a2d3a",
            scrollbar_button_hover_color="#4dd9c0"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        fs = self.fs  # font scale helper

        ctk.CTkLabel(self.scroll_frame, text="Log Workout",
                     font=ctk.CTkFont(size=fs(28), weight="bold"),
                     text_color="#e0e0e0"
                     ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        ctk.CTkLabel(self.scroll_frame, text="RECORD YOUR SESSION DETAILS",
                     font=ctk.CTkFont(size=fs(10)), text_color="#555"
                     ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 24))

        # Error banner (hidden until needed)
        self._error_frame = ctk.CTkFrame(
            self.scroll_frame, fg_color="#2a1a1a",
            border_color="#d9534f", border_width=1, corner_radius=8)
        self._error_label = ctk.CTkLabel(
            self._error_frame, text="",
            font=ctk.CTkFont(size=fs(12)), text_color="#ff6b6b", anchor="w",
            wraplength=700)
        self._error_label.pack(padx=14, pady=10, anchor="w")
        # Not gridded yet — shown on demand

        def field_col(parent, label, required=True):
            """Returns (outer_frame, inner_frame) — put widget in inner_frame."""
            outer = ctk.CTkFrame(parent, fg_color="transparent")
            lbl_row = ctk.CTkFrame(outer, fg_color="transparent")
            lbl_row.pack(fill="x")
            ctk.CTkLabel(lbl_row, text=label,
                         font=ctk.CTkFont(size=fs(12), weight="bold"),
                         text_color="#ccc", anchor="w").pack(side="left")
            if required:
                ctk.CTkLabel(lbl_row, text=" *",
                             font=ctk.CTkFont(size=fs(12)),
                             text_color="#4dd9c0").pack(side="left")
            return outer

        def entry(parent, placeholder, **kwargs):
            return ctk.CTkEntry(
                parent, placeholder_text=placeholder,
                fg_color="#1a1d27", border_color="#2a2d3a",
                text_color="#e0e0e0", placeholder_text_color="#555",
                height=44, font=ctk.CTkFont(size=fs(13)), **kwargs)

        def combo(parent, values, **kwargs):
            return ctk.CTkComboBox(
                parent, values=values,
                fg_color="#1a1d27", border_color="#2a2d3a",
                button_color="#2a2d3a", button_hover_color="#4dd9c0",
                dropdown_fg_color="#1a1d27", text_color="#e0e0e0",
                height=44, font=ctk.CTkFont(size=fs(13)), **kwargs)

     
        def section_hdr(text, row):
            ctk.CTkLabel(self.scroll_frame, text=text,
                         font=ctk.CTkFont(size=fs(15), weight="bold"),
                         text_color="#4dd9c0"
                         ).grid(row=row, column=0, columnspan=2,
                                sticky="w", pady=(20, 12))

        
        section_hdr("Workout Info", 2)

        # Row 3 — Workout Type
        wt_col = field_col(self.scroll_frame, "Workout Type")
        wt_col.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))
        ctk.CTkLabel(wt_col, text="Choose the type of exercise you did",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.workout_type = combo(wt_col,
            ["Cardio", "Strength", "HIIT", "Yoga", "Cycling", "Running", "Swimming"])
        self.workout_type.pack(fill="x", pady=(4, 0))
        self.workout_type.set("Select workout type")

        
        dur_col = field_col(self.scroll_frame, "Duration (minutes)")
        dur_col.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(0, 14))
        ctk.CTkLabel(dur_col, text="How long your session lasted in minutes",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.duration = entry(dur_col, "e.g. 45")
        self.duration.pack(fill="x", pady=(4, 0))

        
        perf_col = field_col(self.scroll_frame, "Workout Performance  (1 = poor, 10 = best)")
        perf_col.grid(row=4, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))
        ctk.CTkLabel(perf_col, text="How well did you perform during this session?",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.workout_performance = combo(perf_col,
            ["1","2","3","4","5","6","7","8","9","10"])
        self.workout_performance.pack(fill="x", pady=(4, 0))
        self.workout_performance.set("Rate your session")

        
        en_col = field_col(self.scroll_frame, "Energy Level  (1 = drained, 10 = energised)")
        en_col.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=(0, 14))
        ctk.CTkLabel(en_col, text="How energised did you feel throughout?",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.energy_level = combo(en_col,
            ["1","2","3","4","5","6","7","8","9","10"])
        self.energy_level.pack(fill="x", pady=(4, 0))
        self.energy_level.set("Rate your energy")

        
        bpm_col = field_col(self.scroll_frame, "Average BPM (optional)", required=False)
        bpm_col.grid(row=5, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))
        ctk.CTkLabel(bpm_col, text="Only if you have a fitness watch or tracker",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.bpm_field = entry(bpm_col, "e.g. 145")
        self.bpm_field.pack(fill="x", pady=(4, 0))

        cal_col = field_col(self.scroll_frame, "Calories Burned (optional)", required=False)
        cal_col.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=(0, 14))
        ctk.CTkLabel(cal_col, text="Enter if shown on your device or app",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.calories_field = entry(cal_col, "e.g. 420")
        self.calories_field.pack(fill="x", pady=(4, 0))

        
        section_hdr("Music Info", 6)

        # Row 7 — Artist
        art_col = field_col(self.scroll_frame, "Top Artist")
        art_col.grid(row=7, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))
        ctk.CTkLabel(art_col, text="Start typing — suggestions will appear",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.top_artist = entry(art_col, "e.g. Dave")
        self.top_artist.pack(fill="x", pady=(4, 0))
        self.top_artist.bind("<KeyRelease>", self.on_artist_typing)

        
        gen_col = field_col(self.scroll_frame, "Genre")
        gen_col.grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=(0, 14))
        ctk.CTkLabel(gen_col, text="The genre of music you trained to",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.genre = entry(gen_col, "e.g. Rap, Afrobeats, Pop")
        self.genre.pack(fill="x", pady=(4, 0))

        
        pl_col = field_col(self.scroll_frame, "Playlist Name")
        pl_col.grid(row=9, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))
        ctk.CTkLabel(pl_col, text="The playlist you used during this session",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.playlist_name = entry(pl_col, "e.g. Beast Mode")
        self.playlist_name.pack(fill="x", pady=(4, 0))

        # Row 9 — Favourite Song
        song_col = field_col(self.scroll_frame, "Favourite Song", required=False)
        song_col.grid(row=9, column=1, sticky="ew", padx=(10, 0), pady=(0, 14))
        ctk.CTkLabel(song_col, text="The track that pushed you hardest today",
                     font=ctk.CTkFont(size=fs(10)), text_color="#444").pack(anchor="w")
        self.fav_song = entry(song_col, "Start typing to search")
        self.fav_song.pack(fill="x", pady=(4, 0))
        self.fav_song.bind("<KeyRelease>", self.on_song_typing)

        
        template_card = ctk.CTkFrame(
            self.scroll_frame, fg_color="#13151f",
            border_color="#2a3340", border_width=1, corner_radius=12)
        template_card.grid(row=10, column=0, columnspan=2,
                           sticky="ew", pady=(24, 8))

        t_left = ctk.CTkFrame(template_card, fg_color="transparent")
        t_left.pack(side="left", fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(t_left, text="📋  Log multiple sessions at once",
                     font=ctk.CTkFont(size=fs(13), weight="bold"),
                     text_color="#e5e5e5", anchor="w").pack(anchor="w")
        ctk.CTkLabel(t_left,
                     text="Download the Excel template, fill in your sessions row by row,\n"
                          "then upload the file using the button below.",
                     font=ctk.CTkFont(size=fs(11)), text_color="#666",
                     anchor="w", justify="left").pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(
            template_card,
            text="⬇  Download Template",
            fg_color="#4dd9c0", hover_color="#3bbfaa",
            text_color="#0f1117", width=180, height=38,
            font=ctk.CTkFont(size=fs(12), weight="bold"),
            command=self.download_template
        ).pack(side="right", padx=20, pady=16)

        # ── OR divider ────────────────────────────────────────────
        or_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        or_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(16, 14))
        or_frame.grid_columnconfigure(0, weight=1)
        or_frame.grid_columnconfigure(2, weight=1)
        ctk.CTkFrame(or_frame, fg_color="#2a2d3a", height=1
                     ).grid(row=0, column=0, sticky="ew", padx=(0, 12))
        ctk.CTkLabel(or_frame, text="OR upload filled template",
                     font=ctk.CTkFont(size=fs(11)), text_color="#555"
                     ).grid(row=0, column=1)
        ctk.CTkFrame(or_frame, fg_color="#2a2d3a", height=1
                     ).grid(row=0, column=2, sticky="ew", padx=(12, 0))

        # Upload button
        ctk.CTkButton(
            self.scroll_frame,
            text="📁  Upload Filled Template",
            fg_color="transparent", border_color="#2a2d3a", border_width=1,
            hover_color="#1e2130", text_color="#888", height=44,
            font=ctk.CTkFont(size=fs(13)),
            command=self.upload_file
        ).grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        # ── Log Session button ────────────────────────────────────
        ctk.CTkButton(
            self.scroll_frame,
            text="Log Session  →",
            fg_color="#4dd9c0", hover_color="#2a7a6e",
            text_color="#0f1117", height=52,
            font=ctk.CTkFont(size=fs(14), weight="bold"),
            command=self.save_session
        ).grid(row=13, column=0, columnspan=2, sticky="ew", pady=(4, 20))

    def download_template(self):
        """Save the Excel template to a user-chosen location."""
        # Build the template
        template_df = pd.DataFrame(columns=[
            "Date", "Workout_Type", "Duration", "Performance",
            "Energy_Level", "Artist", "Genre", "Playlist",
            "Favourite_Song", "BPM", "Calories"
        ])
        # Add one example row
        template_df.loc[0] = [
            datetime.now().strftime("%Y-%m-%d"),
            "Cardio", "45", "8", "7",
            "Dave", "Rap", "Beast Mode", "Sprinter", "155", "380"
        ]
        dest = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx")],
            initialfile="AVANCE_Session_Template.xlsx",
            title="Save AVANCE Template"
        )
        if dest:
            template_df.to_excel(dest, index=False)
            # Confirm
            ok = ctk.CTkToplevel(self)
            ok.title("Template saved")
            ok.geometry("380x140")
            ok.configure(fg_color="#13151f")
            ok.lift(); ok.attributes("-topmost", True)
            ctk.CTkLabel(ok, text="✅  Template saved!",
                         font=ctk.CTkFont(size=15, weight="bold"),
                         text_color="#4dd9c0").pack(pady=(28, 4))
            ctk.CTkLabel(ok, text="Fill it in and upload it using the button above.",
                         font=ctk.CTkFont(size=12), text_color="#888").pack()
            ctk.CTkButton(ok, text="OK", width=80,
                          fg_color="#4dd9c0", text_color="#0f1117",
                          command=ok.destroy).pack(pady=14)

    def show_error(self, message):
        """Display error banner on the log workout form."""
        self._error_label.configure(text=f"⚠  {message}")
        self._error_frame.grid(row=2, column=0, columnspan=2,
                               sticky="ew", pady=(0, 14))
        self._error_frame.lift()

    def hide_error(self):
        self._error_frame.grid_forget()


    
    # ========== LAST.FM API FUNCTIONS ==========
    def search_artist(self, artist_name):
        """Search for artists on Last.fm"""
        if len(artist_name) < 2:
            return []
        
        params = {
            'method': 'artist.search',
            'artist': artist_name,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            'limit': 10
        }
        
        try:
            response = requests.get(LASTFM_BASE_URL, params=params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and 'artistmatches' in data['results']:
                    artists = data['results']['artistmatches']['artist']
                    artist_names = [artist['name'] for artist in artists]
                    
                    # Prioritize exact matches
                    exact_matches = []
                    close_matches = []
                    other_matches = []
                    
                    search_lower = artist_name.lower()
                    
                    for name in artist_names:
                        name_lower = name.lower()
                        if name_lower == search_lower:
                            exact_matches.append(name)
                        elif name_lower.startswith(search_lower):
                            close_matches.append(name)
                        else:
                            other_matches.append(name)
                    
                    sorted_results = exact_matches + close_matches + other_matches
                    return sorted_results[:5]
        except:
            print("⚠️ API request failed")
        
        return []
    
    def search_track(self, track_name, artist_name=""):
        """Search for tracks on Last.fm"""
        if len(track_name) < 2:
            return []
        
        params = {
            'method': 'track.search',
            'track': track_name,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            'limit': 5
        }
        
        if artist_name:
            params['artist'] = artist_name
        
        try:
            response = requests.get(LASTFM_BASE_URL, params=params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and 'trackmatches' in data['results']:
                    tracks = data['results']['trackmatches']['track']
                    return [f"{track['name']} - {track['artist']}" for track in tracks[:5]]
        except:
            print("⚠️ Track search failed")
        
        return []
    
    def get_artist_info(self, artist_name):
        """Get artist info including tags"""
        params = {
            'method': 'artist.getinfo',
            'artist': artist_name,
            'api_key': LASTFM_API_KEY,
            'format': 'json'
        }
        
        try:
            response = requests.get(LASTFM_BASE_URL, params=params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if 'artist' in data:
                    artist = data['artist']
                    tags = []
                    if 'tags' in artist and 'tag' in artist['tags']:
                        tags = [tag['name'] for tag in artist['tags']['tag'][:5]]
                    
                    return {'name': artist['name'], 'tags': tags}
        except:
            print("⚠️ API request failed")
        
        return None
    
    def on_artist_typing(self, event):
        """Called when user types in artist field"""
        typed_text = self.top_artist.get().strip()
        
        if len(typed_text) < 2:
            self.hide_artist_dropdown()
            return
        
        suggestions = self.search_artist(typed_text)
        
        if suggestions:
            self.show_artist_dropdown(suggestions)
        else:
            self.hide_artist_dropdown()
    
    def on_song_typing(self, event):
        """Called when user types in song field"""
        typed_text = self.fav_song.get().strip()
        artist_name = self.top_artist.get().strip()
        
        if len(typed_text) < 2:
            self.hide_song_dropdown()
            return
        
        suggestions = self.search_track(typed_text, artist_name)
        
        if suggestions:
            self.show_song_dropdown(suggestions)
        else:
            self.hide_song_dropdown()
    
    def show_artist_dropdown(self, suggestions):
        """Display artist dropdown"""
        self.hide_artist_dropdown()
        
        self.artist_dropdown = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#1a1d27",
            border_color="#4dd9c0",
            border_width=1,
            corner_radius=6
        )
        self.artist_dropdown.grid(row=7, column=0, columnspan=2, sticky="ew", padx=(0, 0), pady=(0, 10))
        
        for artist in suggestions[:5]:
            btn = ctk.CTkButton(
                self.artist_dropdown,
                text=artist,
                fg_color="transparent",
                hover_color="#2a2d3a",
                text_color="#e0e0e0",
                anchor="w",
                height=35,
                font=ctk.CTkFont(size=12),
                command=lambda a=artist: self.select_artist(a)
            )
            btn.pack(fill="x", padx=5, pady=2)
    
    def show_song_dropdown(self, suggestions):
        """Display song dropdown"""
        self.hide_song_dropdown()
        
        self.song_dropdown = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#1a1d27",
            border_color="#4dd9c0",
            border_width=1,
            corner_radius=6
        )
        self.song_dropdown.grid(row=9, column=0, columnspan=2, sticky="ew", padx=(0, 0), pady=(0, 10))
        
        for song in suggestions[:5]:
            btn = ctk.CTkButton(
                self.song_dropdown,
                text=song,
                fg_color="transparent",
                hover_color="#2a2d3a",
                text_color="#e0e0e0",
                anchor="w",
                height=35,
                font=ctk.CTkFont(size=12),
                command=lambda s=song: self.select_song(s)
            )
            btn.pack(fill="x", padx=5, pady=2)
    
    def hide_artist_dropdown(self):
        """Hide artist dropdown"""
        if hasattr(self, 'artist_dropdown'):
            self.artist_dropdown.destroy()
            delattr(self, 'artist_dropdown')
    
    def hide_song_dropdown(self):
        """Hide song dropdown"""
        if hasattr(self, 'song_dropdown'):
            self.song_dropdown.destroy()
            delattr(self, 'song_dropdown')
    
    def select_artist(self, artist_name):
        """User selected an artist"""
        self.top_artist.delete(0, 'end')
        self.top_artist.insert(0, artist_name)
        self.hide_artist_dropdown()
        
        print(f"🔍 Getting info for {artist_name}...")
        info = self.get_artist_info(artist_name)
        
        if info and info['tags']:
            genre = info['tags'][0]
            self.genre.delete(0, 'end')
            self.genre.insert(0, genre.title())
            print(f"✅ Auto-filled genre: {genre}")
    
    def select_song(self, song_text):
        """User selected a song"""
        # Extract just the song name (before " - ")
        song_name = song_text.split(" - ")[0]
        self.fav_song.delete(0, 'end')
        self.fav_song.insert(0, song_name)
        self.hide_song_dropdown()
    
    # ========== FILE UPLOAD ==========
    def upload_file(self):
        """Handle CSV/Excel file upload with confirmation dialogs"""
        file_path = filedialog.askopenfilename(
            title="Select workout data file",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        def show_popup(icon, title, lines, btn_color="#4dd9c0", btn_text_color="#0f1117"):
            popup = ctk.CTkToplevel(self)
            popup.title(title)
            popup.geometry("420x200")
            popup.configure(fg_color="#13151f")
            popup.lift()
            popup.attributes("-topmost", True)
            popup.grab_set()
            # Centre it
            popup.update_idletasks()
            sw = popup.winfo_screenwidth()
            sh = popup.winfo_screenheight()
            x = (sw - 420) // 2
            y = (sh - 200) // 2
            popup.geometry(f"420x200+{x}+{y}")

            ctk.CTkLabel(popup, text=icon, font=ctk.CTkFont(size=36)).pack(pady=(22, 4))
            for i, line in enumerate(lines):
                ctk.CTkLabel(popup, text=line,
                             font=ctk.CTkFont(size=13 if i == 0 else 11,
                                              weight="bold" if i == 0 else "normal"),
                             text_color="#e5e5e5" if i == 0 else "#888",
                             wraplength=360).pack(pady=(0, 2))
            ctk.CTkButton(
                popup, text="OK", width=100, height=34,
                fg_color=btn_color, text_color=btn_text_color,
                hover_color="#3bbfaa",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=popup.destroy
            ).pack(pady=(14, 0))

        try:
            if file_path.endswith('.csv'):
                uploaded_df = pd.read_csv(file_path)
            else:
                uploaded_df = pd.read_excel(file_path)

            required_cols = ["Date", "Workout_Type", "Duration", "Performance",
                             "Energy_Level", "Playlist", "Genre", "Artist", "Fav_Song"]

            missing_cols = [c for c in required_cols if c not in uploaded_df.columns]
            if missing_cols:
                show_popup(
                    "⚠️", "Invalid File",
                    [
                        "This file is missing required columns.",
                        "Missing: " + ", ".join(missing_cols),
                        "Please use the AVANCE template and try again."
                    ],
                    btn_color="#d9534f", btn_text_color="#fff"
                )
                return

            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_file = os.path.join(script_dir, "workout_data.csv")

            before_count = 0
            if os.path.exists(csv_file):
                existing_df = pd.read_csv(csv_file)
                before_count = len(existing_df)
                merged_df = pd.concat([existing_df, uploaded_df], ignore_index=True)
                merged_df = merged_df.drop_duplicates()
                merged_df.to_csv(csv_file, index=False)
                added = len(merged_df) - before_count
                total = len(merged_df)
            else:
                uploaded_df.to_csv(csv_file, index=False)
                added = len(uploaded_df)
                total = added

            show_popup(
                "✅", "Upload Successful",
                [
                    f"{added} session{'s' if added != 1 else ''} imported successfully!",
                    f"You now have {total} session{'s' if total != 1 else ''} logged in total.",
                    "Head to Dashboard or Insights to see your updated stats."
                ]
            )

        except Exception as e:
            show_popup(
                "❌", "Upload Failed",
                [
                    "Something went wrong while reading your file.",
                    str(e)[:120],
                    "Make sure the file is not open in another program."
                ],
                btn_color="#d9534f", btn_text_color="#fff"
            )

    
    def save_session(self):
        """Save workout session to CSV with validation."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(script_dir, "workout_data.csv")

        wt    = self.workout_type.get()
        dur   = self.duration.get().strip()
        perf  = self.workout_performance.get()
        energy = self.energy_level.get()
        artist = self.top_artist.get().strip()
        genre  = self.genre.get().strip()
        playlist = self.playlist_name.get().strip()

        missing = []
        if wt in ("Select workout type", ""):
            missing.append("Workout Type")
        if not dur:
            missing.append("Duration")
        elif not dur.isdigit():
            self.show_error("Duration must be a number (e.g. 45)")
            return
        if perf in ("Rate your session", ""):
            missing.append("Workout Performance")
        if energy in ("Rate your energy", ""):
            missing.append("Energy Level")
        if not artist:
            missing.append("Top Artist")
        if not genre:
            missing.append("Genre")
        if not playlist:
            missing.append("Playlist Name")

        if missing:
            self.show_error(
                "Please complete the following required fields: "
                + ", ".join(missing)
            )
            return

        self.hide_error()

        session_data = {
            "Date":         datetime.now().strftime("%Y-%m-%d"),
            "Workout_Type": wt,
            "Duration":     dur,
            "Performance":  perf,
            "Energy_Level": energy,
            "Playlist":     playlist,
            "Genre":        genre,
            "Artist":       artist,
            "Fav_Song":     self.fav_song.get().strip(),
            "BPM":          self.bpm_field.get().strip(),
            "Calories":     self.calories_field.get().strip(),
        }

        df = pd.DataFrame([session_data])
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode="a", header=False, index=False)
        else:
            df.to_csv(csv_file, index=False)

        self.clear_form()

        # ── Success toast ─────────────────────────────────────────
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.configure(fg_color="#1a3a2a")
        toast.attributes("-topmost", True)
        sw, sh = toast.winfo_screenwidth(), toast.winfo_screenheight()
        toast.geometry(f"320x56+{(sw-320)//2}+{sh-120}")
        ctk.CTkLabel(toast, text="✅  Session logged successfully!",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#4dd9c0").pack(expand=True)
        toast.after(2200, toast.destroy)

    def clear_form(self):
        """Clear all input fields after saving."""
        self.workout_type.set("Select workout type")
        self.duration.delete(0, "end")
        self.workout_performance.set("Rate your session")
        self.energy_level.set("Rate your energy")
        self.playlist_name.delete(0, "end")
        self.genre.delete(0, "end")
        self.top_artist.delete(0, "end")
        self.fav_song.delete(0, "end")
        self.bpm_field.delete(0, "end")
        self.calories_field.delete(0, "end")



    def show_dashboard(self):
        """Dashboard page with stats and charts"""
        self.clear_main_frame()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(script_dir, "workout_data.csv")
        
        if not os.path.exists(csv_file):
            no_data = ctk.CTkLabel(
                self.main_frame,
                text="No data yet!\nLog your first workout to see your dashboard.",
                font=ctk.CTkFont(size=16),
                text_color="#888"
            )
            no_data.pack(pady=100)
            return
        
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="#0f1117",
            scrollbar_button_color="#2a2d3a",
            scrollbar_button_hover_color="#4dd9c0"
        )
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            scroll_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#e0e0e0"
        )
        title.pack(anchor="w", pady=(0, 5))
        
        subtitle = ctk.CTkLabel(
            scroll_frame,
            text="YOUR PERFORMANCE OVERVIEW",
            font=ctk.CTkFont(size=10),
            text_color="#555"
        )
        subtitle.pack(anchor="w", pady=(0, 20))
        
        # STREAK TRACKER
        streak_days = self.calculate_streak(df)
        max_streak = self.calculate_max_streak(df)
        
        streak_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color="#202433",
            border_color="#41E3D8",
            border_width=1,
            corner_radius=10
        )
        streak_frame.pack(fill="x", pady=(0, 20))
        
        streak_content = ctk.CTkFrame(streak_frame, fg_color="transparent")
        streak_content.pack(fill="x", padx=20, pady=15)
        
        left_frame = ctk.CTkFrame(streak_content, fg_color="transparent")
        left_frame.pack(side="left")
        
        flame_label = ctk.CTkLabel(left_frame, text="🔥", font=ctk.CTkFont(size=40))
        flame_label.pack(side="left", padx=(0, 15))
        
        streak_info = ctk.CTkFrame(left_frame, fg_color="transparent")
        streak_info.pack(side="left")
        
        streak_number = ctk.CTkLabel(
            streak_info,
            text=str(streak_days),
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#4dd9c0"
        )
        streak_number.pack(anchor="w")
        
        streak_label = ctk.CTkLabel(
            streak_info,
            text="DAY STREAK",
            font=ctk.CTkFont(size=11),
            text_color="#888"
        )
        streak_label.pack(anchor="w")
        
        right_frame = ctk.CTkFrame(streak_content, fg_color="transparent")
        right_frame.pack(side="right")
        
        best_label = ctk.CTkLabel(
            right_frame,
            text=f"Personal best: {max_streak} days",
            font=ctk.CTkFont(size=11),
            text_color="#666"
        )
        best_label.pack(anchor="e")
        
        if streak_days < max_streak:
            days_to_beat = max_streak - streak_days + 1
            motivation = ctk.CTkLabel(
                right_frame,
                text=f"{days_to_beat} days to beat your record!",
                font=ctk.CTkFont(size=10),
                text_color="#4dd9c0"
            )
            motivation.pack(anchor="e")
        
        # STATS CARDS
        stats_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        total_sessions = len(df)
        total_mins = df['Duration'].astype(str).str.extract('(\d+)')[0].astype(float).sum()
        avg_performance = df['Performance'].astype(str).str.extract('(\d+)')[0].astype(float).mean()
        top_genre = df['Genre'].mode()[0] if len(df['Genre'].mode()) > 0 else "N/A"
        
        stats = [
            ("Total Sessions", str(total_sessions), f"↑ {len(df[df['Date'] >= (datetime.now() - pd.Timedelta(days=7))])} this week"),
            ("Total Minutes", f"{int(total_mins)}", f"Avg {int(total_mins/total_sessions)} min"),
            ("Avg Performance", f"{avg_performance:.1f}/10", "Quality score"),
            ("Top Genre", top_genre[:12], f"{int((df['Genre'] == top_genre).sum() / len(df) * 100)}% of sessions")
        ]
        
        for i, (label, value, sub) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color="#1a1d27", corner_radius=8)
            card.pack(side="left", fill="both", expand=True, padx=5 if i < 3 else 0)
            
            stat_label = ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=10), text_color="#888")
            stat_label.pack(pady=(15, 5))
            
            stat_value = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color="#4dd9c0")
            stat_value.pack()
            
            stat_sub = ctk.CTkLabel(card, text=sub, font=ctk.CTkFont(size=9), text_color="#555")
            stat_sub.pack(pady=(5, 15))
        
        # CHARTS
        charts_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True)
        
        # Chart 1: Workout Types
        chart1_frame = ctk.CTkFrame(charts_frame, fg_color="#1a1d27", corner_radius=8)
        chart1_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        chart1_title = ctk.CTkLabel(chart1_frame, text="Workouts by Type", font=ctk.CTkFont(size=12, weight="bold"), text_color="#888")
        chart1_title.pack(pady=(15, 10))
        
        self.create_workout_chart(chart1_frame, df)
        
        # Chart 2: Genre Distribution
        chart2_frame = ctk.CTkFrame(charts_frame, fg_color="#1a1d27", corner_radius=8)
        chart2_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        chart2_title = ctk.CTkLabel(chart2_frame, text="Genre Distribution", font=ctk.CTkFont(size=12, weight="bold"), text_color="#888")
        chart2_title.pack(pady=(15, 10))
        
        self.create_genre_chart(chart2_frame, df)
        
        # Chart 3: Quality Over Time
        chart3_frame = ctk.CTkFrame(charts_frame, fg_color="#1a1d27", corner_radius=8)
        chart3_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        chart3_title = ctk.CTkLabel(chart3_frame, text="Quality Over Time", font=ctk.CTkFont(size=12, weight="bold"), text_color="#888")
        chart3_title.pack(pady=(15, 10))
        
        self.create_quality_chart(chart3_frame, df)
    
    
    def create_workout_chart(self, parent, df):
        """Bar chart for workout types"""
        workout_counts = df['Workout_Type'].value_counts()
        
        fig = Figure(figsize=(3.5, 2.5), facecolor='#1a1d27')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1d27')
        
        bars = ax.bar(range(len(workout_counts)), workout_counts.values, color='#4dd9c0', alpha=0.7)
        max_idx = workout_counts.values.argmax()
        bars[max_idx].set_alpha(1.0)
        
        ax.set_xticks(range(len(workout_counts)))
        ax.set_xticklabels([w[:8] for w in workout_counts.index], rotation=45, ha='right', fontsize=8, color='#888')
        ax.tick_params(axis='y', labelsize=8, colors='#888')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#2a2d3a')
        ax.spines['bottom'].set_color('#2a2d3a')
        ax.grid(axis='y', alpha=0.2, color='#2a2d3a')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=(0, 10))
    
    def create_genre_chart(self, parent, df):
        """Pie chart for genre distribution"""
        genre_counts = df['Genre'].value_counts().head(4)
        
        fig = Figure(figsize=(3.5, 2.5), facecolor='#1a1d27')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1d27')
        
        colors = ['#4dd9c0', '#2a7a6e', '#1a4a44', '#555']
        wedges, texts, autotexts = ax.pie(
            genre_counts.values,
            labels=genre_counts.index,
            colors=colors,
            autopct='%1.0f%%',
            startangle=90,
            textprops={'color': '#e0e0e0', 'fontsize': 9}
        )
        
        for autotext in autotexts:
            autotext.set_color('#0f1117')
            autotext.set_fontsize(8)
            autotext.set_weight('bold')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=(0, 10))
    
    def create_quality_chart(self, parent, df):
        """Line chart for quality over time"""
        df_sorted = df.sort_values('Date')
        quality = df_sorted['Performance'].astype(str).str.extract('(\d+)')[0].astype(float)
        
        fig = Figure(figsize=(3.5, 2.5), facecolor='#1a1d27')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1d27')
        
        ax.plot(range(len(quality)), quality.values, color='#4dd9c0', linewidth=2, marker='o', markersize=4)
        ax.fill_between(range(len(quality)), quality.values, alpha=0.2, color='#4dd9c0')
        
        ax.set_xlim(-0.5, len(quality) - 0.5)
        ax.set_ylim(0, 11)
        ax.tick_params(axis='both', labelsize=8, colors='#888')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#2a2d3a')
        ax.spines['bottom'].set_color('#2a2d3a')
        ax.grid(axis='y', alpha=0.2, color='#2a2d3a')
        ax.set_xticks([])
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=(0, 10))
    
    # ========== STREAK FUNCTIONS ==========
    def calculate_streak(self, df):
        """Calculate current streak"""
        if len(df) == 0:
            return 0
        
        df_sorted = df.sort_values('Date', ascending=False)
        dates = df_sorted['Date'].dt.date.unique()
        
        today = datetime.now().date()
        yesterday = today - pd.Timedelta(days=1)
        
        if dates[0] not in [today, yesterday]:
            return 0
        
        streak = 1
        current_date = dates[0]
        
        for i in range(1, len(dates)):
            expected_date = current_date - pd.Timedelta(days=1)
            if dates[i] == expected_date:
                streak += 1
                current_date = dates[i]
            else:
                break
        
        return streak
    
    def calculate_max_streak(self, df):
        """Calculate longest streak ever"""
        if len(df) == 0:
            return 0
        
        df_sorted = df.sort_values('Date')
        dates = df_sorted['Date'].dt.date.unique()
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] + pd.Timedelta(days=1):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    # ========== INSIGHTS PAGE (STYLED LIKE FIGMA) ==========
    def show_insights(self):
        """Insights page - exactly matching Figma design"""
        self.clear_main_frame()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(script_dir, "workout_data.csv")
        
        if not os.path.exists(csv_file):
            no_data = ctk.CTkLabel(
                self.main_frame,
                text="No data yet!\nLog workouts to see insights.",
                font=ctk.CTkFont(size=16),
                text_color="#888"
            )
            no_data.pack(pady=100)
            return
        
        df = pd.read_csv(csv_file)
        
        if len(df) < 1:
            no_data = ctk.CTkLabel(
                self.main_frame,
                text="No data yet!\nLog your first workout to see insights.",
                font=ctk.CTkFont(size=16),
                text_color="#888"
            )
            no_data.pack(pady=100)
            return
        
        # Scrollable frame - SAME PADDING AS OTHER PAGES
        scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="#0f1117",
            scrollbar_button_color="#2a2d3a",
            scrollbar_button_hover_color="#4dd9c0"
        )
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            scroll_frame,
            text="Insights",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#e0e0e0"
        )
        title.pack(anchor="w", pady=(0, 5))
        
        subtitle = ctk.CTkLabel(
            scroll_frame,
            text="RECORD YOUR SESSION DETAILS",
            font=ctk.CTkFont(size=10),
            text_color="#555"
        )
        subtitle.pack(anchor="w", pady=(0, 30))
        
        # ========== 1. COMBINED INSIGHTS SECTION ==========
        insights_container = ctk.CTkFrame(
            scroll_frame,
            fg_color="#13151f",
            border_color="#2a3f4a",
            border_width=1,
            corner_radius=15,
            height=280
        )
        insights_container.pack(fill="x", pady=(0, 20))
        insights_container.pack_propagate(False)
        
        # Header with fire emoji
        header_frame = ctk.CTkFrame(insights_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 15))
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(anchor="w")
        
        fire_icon = ctk.CTkLabel(
            header_content,
            text="🔥",
            font=ctk.CTkFont(size=16)
        )
        fire_icon.pack(side="left", padx=(0, 8))
        
        insights_title = ctk.CTkLabel(
            header_content,
            text="Combined Insights",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4dd9c0"
        )
        insights_title.pack(side="left")
        
        # Generate insights
        insights = self.generate_figma_insights(df)
        
        # Display insights with cyan bullets
        for insight in insights:
            row = ctk.CTkFrame(insights_container, fg_color="transparent")
            row.pack(fill="x", padx=25, pady=6)
            
            bullet = ctk.CTkLabel(
                row,
                text="●",
                font=ctk.CTkFont(size=11),
                text_color="#4dd9c0"
            )
            bullet.pack(side="left", padx=(0, 12))
            
            text = ctk.CTkLabel(
                row,
                text=insight,
                font=ctk.CTkFont(size=12),
                text_color="#b5b5b5",
                wraplength=1050,
                justify="left"
            )
            text.pack(side="left", anchor="w", fill="x", expand=True)
        
        ctk.CTkLabel(insights_container, text="", height=15).pack()
        
        # ========== 2. RECOMMENDED ARTISTS SECTION ==========
        top_artist = self.get_top_performing_artist(df)
        
        if top_artist:
            artists_container = ctk.CTkFrame(
                scroll_frame,
                fg_color="#13151f",
                border_color="#2a3f4a",
                border_width=1,
                corner_radius=15,
                height=280
            )
            artists_container.pack(fill="x", pady=(0, 20))
            artists_container.pack_propagate(False)
            
            # Header with headphone emoji
            header_frame2 = ctk.CTkFrame(artists_container, fg_color="transparent")
            header_frame2.pack(fill="x", padx=25, pady=(20, 5))
            
            header_content2 = ctk.CTkFrame(header_frame2, fg_color="transparent")
            header_content2.pack(anchor="w")
            
            headphone_icon = ctk.CTkLabel(
                header_content2,
                text="🎧",
                font=ctk.CTkFont(size=16)
            )
            headphone_icon.pack(side="left", padx=(0, 8))
            
            artists_title = ctk.CTkLabel(
                header_content2,
                text="Recommended Artist:",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4dd9c0"
            )
            artists_title.pack(side="left")
            
            subtitle2 = ctk.CTkLabel(
                header_frame2,
                text=f"Similar artists that may boost your sessions Based on your top performer",
                font=ctk.CTkFont(size=11),
                text_color="#6a6a6a"
            )
            subtitle2.pack(anchor="w", pady=(3, 18))
            
            # Get similar artists
            similar_artists = self.get_similar_artists(top_artist)
            
            if similar_artists and len(similar_artists) >= 1:
                cards_row = ctk.CTkFrame(artists_container, fg_color="transparent")
                cards_row.pack(fill="x", padx=25, pady=(0, 20))

                for i, artist_info in enumerate(similar_artists[:3]):
                    # Artist card
                    card = ctk.CTkFrame(
                        cards_row,
                        fg_color="#1a1f2e",
                        corner_radius=15,
                        border_color="#2a3340",
                        border_width=1
                    )
                    card.pack(side="left", fill="both", expand=True, padx=(0, 10) if i < 2 else 0)

                    # Inner row: circle icon on left, name+tags on right
                    inner = ctk.CTkFrame(card, fg_color="transparent")
                    inner.pack(fill="x", padx=18, pady=22)

                    # Music note circle
                    note_circle = ctk.CTkLabel(
                        inner,
                        text="♫",
                        font=ctk.CTkFont(size=26),
                        text_color="#4dd9c0",
                        fg_color="#1e2d3a",
                        width=65,
                        height=65,
                        corner_radius=33
                    )
                    note_circle.pack(side="left", padx=(0, 14))

                    # Right side: name + tags stacked
                    right_col = ctk.CTkFrame(inner, fg_color="transparent")
                    right_col.pack(side="left", fill="both", expand=True)

                    name_lbl = ctk.CTkLabel(
                        right_col,
                        text=artist_info['name'],
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color="#e5e5e5",
                        anchor="w",
                        wraplength=120
                    )
                    name_lbl.pack(anchor="w", pady=(0, 8))

                    if artist_info.get('tags'):
                        tags_row = ctk.CTkFrame(right_col, fg_color="transparent")
                        tags_row.pack(anchor="w")
                        for tag in artist_info['tags'][:2]:
                            tag_pill = ctk.CTkLabel(
                                tags_row,
                                text=tag.capitalize()[:12],
                                font=ctk.CTkFont(size=9),
                                text_color="#4dd9c0",
                                fg_color="#1e3030",
                                corner_radius=10,
                                height=22
                            )
                            tag_pill.pack(side="left", padx=(0, 5), ipadx=8)
            else:
                no_artists = ctk.CTkLabel(
                    artists_container,
                    text=f"Could not load similar artists for \"{top_artist}\" — check your internet connection.",
                    font=ctk.CTkFont(size=11),
                    text_color="#555"
                )
                no_artists.pack(padx=25, pady=(0, 20), anchor="w")
        
        # ========== 3. TOP TRACKS SECTION ==========
        if top_artist:
            tracks_container = ctk.CTkFrame(
                scroll_frame,
                fg_color="#13151f",
                border_color="#2a3f4a",
                border_width=1,
                corner_radius=15,
                height=280
            )
            tracks_container.pack(fill="x", pady=(0, 20))
            tracks_container.pack_propagate(False)
            
            # Header with music note emoji
            header_frame3 = ctk.CTkFrame(tracks_container, fg_color="transparent")
            header_frame3.pack(fill="x", padx=25, pady=(20, 15))
            
            header_content3 = ctk.CTkFrame(header_frame3, fg_color="transparent")
            header_content3.pack(anchor="w")
            
            music_icon = ctk.CTkLabel(
                header_content3,
                text="🎵",
                font=ctk.CTkFont(size=16)
            )
            music_icon.pack(side="left", padx=(0, 8))
            
            tracks_title = ctk.CTkLabel(
                header_content3,
                text="Top Tracks for Your Best Artist",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4dd9c0"
            )
            tracks_title.pack(side="left")
            
            # Get tracks
            top_tracks = self.get_top_tracks(top_artist)
            
            if top_tracks:
                fill_values = [1.0, 0.82, 0.68]  # decreasing fill per track
                for i, track in enumerate(top_tracks[:3]):
                    # Separator line between rows
                    if i > 0:
                        sep = ctk.CTkFrame(tracks_container, fg_color="#1e2130", height=1)
                        sep.pack(fill="x", padx=25)

                    # Track row
                    track_row = ctk.CTkFrame(tracks_container, fg_color="transparent", height=50)
                    track_row.pack(fill="x", padx=25, pady=(8, 8))
                    track_row.pack_propagate(False)

                    # Track name
                    name_label = ctk.CTkLabel(
                        track_row,
                        text=track['name'],
                        font=ctk.CTkFont(size=12),
                        text_color="#d5d5d5",
                        anchor="w",
                        width=160
                    )
                    name_label.pack(side="left")

                    # Progress bar — teal fill, dark track
                    progress = ctk.CTkProgressBar(
                        track_row,
                        height=7,
                        corner_radius=4,
                        fg_color="#1a1f2e",
                        progress_color="#4dd9c0"
                    )
                    progress.pack(side="left", fill="x", expand=True, padx=(10, 0))
                    progress.set(fill_values[i])
            
            ctk.CTkLabel(tracks_container, text="", height=15).pack()

   
    def generate_figma_insights(self, df):
        """Generate insights matching Figma examples"""
        insights = []

        df = df.copy()
        df['Performance_Num'] = df['Performance'].astype(str).str.extract(r'(\d+)')[0].astype(float)
        df['Duration_Num'] = df['Duration'].astype(str).str.extract(r'(\d+)')[0].astype(float)

        # Insight 1: Best vs worst genre performance
        try:
            genre_performance = df.groupby('Genre')['Performance_Num'].mean().sort_values(ascending=False)
            if len(genre_performance) >= 2:
                best_genre = genre_performance.index[0]
                best_perf = genre_performance.iloc[0]
                worst_genre = genre_performance.index[-1]
                worst_perf = genre_performance.iloc[-1]
                if worst_perf > 0:
                    diff_pct = int(((best_perf - worst_perf) / worst_perf) * 100)
                    insights.append(f"You perform {diff_pct}% better with {best_genre} — avg quality {best_perf:.1f}/10 vs {worst_perf:.1f} with {worst_genre}.")
                else:
                    insights.append(f"Your top genre is {best_genre} with an avg quality of {best_perf:.1f}/10.")
        except Exception as e:
            print(f"Insight 1 error: {e}")

        # Insight 2: Playlist duration
        try:
            playlist_duration = df.groupby('Playlist')['Duration_Num'].mean().sort_values(ascending=False)
            if len(playlist_duration) > 0:
                longest_playlist = playlist_duration.index[0]
                avg_playlist_dur = playlist_duration.iloc[0]
                overall_avg = df['Duration_Num'].mean()
                insights.append(f'Playlist "{longest_playlist}" is linked to your longest workouts — avg {avg_playlist_dur:.0f} mins vs your {overall_avg:.0f} min overall average.')
        except Exception as e:
            print(f"Insight 2 error: {e}")

        # Insight 3: Streak impact OR consistency trend
        try:
            streak = self.calculate_streak(df)
            if streak >= 3:
                recent_sessions = df.tail(streak)
                recent_perf = recent_sessions['Performance_Num'].mean()
                older = df.head(len(df) - streak)
                older_perf = older['Performance_Num'].mean() if len(older) > 0 else df['Performance_Num'].mean()
                insights.append(f"Your 🔥 {streak}-day streak has pushed your weekly avg quality from {older_perf:.1f} → {recent_perf:.1f}. Consistency is working.")
            else:
                # Fallback: overall performance trend (first half vs second half)
                half = max(1, len(df) // 2)
                early_perf = df.head(half)['Performance_Num'].mean()
                recent_perf = df.tail(half)['Performance_Num'].mean()
                diff = recent_perf - early_perf
                direction = "improved" if diff >= 0 else "dropped"
                insights.append(f"Your performance has {direction} by {abs(diff):.1f} pts compared to your earlier sessions — avg {recent_perf:.1f}/10 recently vs {early_perf:.1f}/10 before.")
        except Exception as e:
            print(f"Insight 3 error: {e}")

        # Insight 4: Best playlist by performance
        try:
            playlist_perf = df.groupby('Playlist')['Performance_Num'].mean()
            if len(playlist_perf) > 0:
                best_playlist = playlist_perf.idxmax()
                best_val = playlist_perf.max()
                insights.append(f'You perform best with the playlist "{best_playlist}" — averaging {best_val:.1f}/10 quality during those sessions.')
        except Exception as e:
            print(f"Insight 4 error: {e}")

        # Insight 5: Best workout type by performance
        try:
            type_perf = df.groupby('Workout_Type')['Performance_Num'].mean().sort_values(ascending=False)
            if len(type_perf) >= 1:
                best_type = type_perf.index[0]
                best_type_val = type_perf.iloc[0]
                total_type_sessions = int((df['Workout_Type'] == best_type).sum())
                insights.append(f"{best_type} is your strongest workout type — avg performance {best_type_val:.1f}/10 across {total_type_sessions} session{'s' if total_type_sessions != 1 else ''}.")
        except Exception as e:
            print(f"Insight 5 error: {e}")

        # Insight 6: Top artist performance
        try:
            artist_perf = df.groupby('Artist')['Performance_Num'].mean().sort_values(ascending=False)
            if len(artist_perf) >= 1:
                top_art = artist_perf.index[0]
                top_art_val = artist_perf.iloc[0]
                insights.append(f'Your sessions with "{top_art}" rank highest — {top_art_val:.1f}/10 avg quality. Consider them your go-to workout artist.')
        except Exception as e:
            print(f"Insight 6 error: {e}")

        # Fallback if nothing generated
        if not insights:
            avg_p = df['Performance_Num'].mean()
            insights.append(f"Your average workout quality is {avg_p:.1f}/10 — keep logging to unlock deeper insights!")

        return insights[:5]
    
    def get_top_performing_artist(self, df):
        """Get artist with best average performance"""
        if len(df) == 0:
            return None
        
        df['Performance_Num'] = df['Performance'].astype(str).str.extract('(\d+)')[0].astype(float)
        artist_perf = df.groupby('Artist')['Performance_Num'].mean().sort_values(ascending=False)
        
        if len(artist_perf) > 0:
            return artist_perf.index[0]
        return None
    
    def get_similar_artists(self, artist_name):
        """Get similar artists from Last.fm"""
        params = {
            'method': 'artist.getsimilar',
            'artist': artist_name,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            'limit': 3
        }
        
        try:
            response = requests.get(LASTFM_BASE_URL, params=params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if 'similarartists' in data and 'artist' in data['similarartists']:
                    artists = data['similarartists']['artist']
                    
                    result = []
                    for artist in artists[:3]:
                        info = self.get_artist_info(artist['name'])
                        if info:
                            result.append(info)
                    
                    return result
        except:
            print("⚠️ Could not fetch similar artists")
        
        return []
    
    def get_top_tracks(self, artist_name):
        """Get top tracks from Last.fm"""
        params = {
            'method': 'artist.gettoptracks',
            'artist': artist_name,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            'limit': 3
        }
        
        try:
            response = requests.get(LASTFM_BASE_URL, params=params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if 'toptracks' in data and 'track' in data['toptracks']:
                    tracks = data['toptracks']['track']
                    return [{'name': track['name']} for track in tracks[:3]]
        except:
            print("⚠️ Could not fetch top tracks")
        
        return []

    # ========== SETTINGS PAGE ==========
    def show_settings(self):
        self._current_page = "Settings"
        scroll = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="#0f1117",
            scrollbar_button_color="#2a2d3a",
            scrollbar_button_hover_color="#4dd9c0"
        )
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        fs = self.fs

        # Title
        ctk.CTkLabel(scroll, text="Settings",
                     font=ctk.CTkFont(size=fs(28), weight="bold"),
                     text_color="#e0e0e0").pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(scroll, text="ACCESSIBILITY",
                     font=ctk.CTkFont(size=fs(10)), text_color="#555").pack(anchor="w", pady=(0, 28))

      
        card = ctk.CTkFrame(scroll, fg_color="#13151f",
                            border_color="#2a3340", border_width=1, corner_radius=14)
        card.pack(fill="x", pady=(0, 16))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=22, pady=(18, 6))
        ctk.CTkLabel(hdr, text="𝐀", font=ctk.CTkFont(size=fs(16)),
                     text_color="#4dd9c0").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(hdr, text="Text Size",
                     font=ctk.CTkFont(size=fs(14), weight="bold"),
                     text_color="#e5e5e5").pack(side="left")

        ctk.CTkFrame(card, fg_color="#2a2d3a", height=1).pack(fill="x", padx=22)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=22, pady=(18, 22))

        # Description + current size badge
        desc_row = ctk.CTkFrame(body, fg_color="transparent")
        desc_row.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(desc_row,
                     text="Adjust how large text appears across the whole app.\nChanges apply immediately when you navigate to any page.",
                     font=ctk.CTkFont(size=fs(12)), text_color="#888",
                     anchor="w", justify="left").pack(side="left")

        self._size_badge = ctk.CTkLabel(
            desc_row,
            text=f"{self.font_size}px",
            font=ctk.CTkFont(size=fs(18), weight="bold"),
            text_color="#4dd9c0", width=58)
        self._size_badge.pack(side="right")

        # Slider
        def on_slide(val):
            size = int(val)
            self.font_size = size
            self._size_badge.configure(text=f"{size}px")
            self.refresh_sidebar_fonts()
            # Update preview label
            preview.configure(font=ctk.CTkFont(size=size))

        slider = ctk.CTkSlider(
            body, from_=11, to=22, number_of_steps=11,
            progress_color="#4dd9c0", button_color="#4dd9c0",
            button_hover_color="#3bbfaa", fg_color="#1a1f2e",
            command=on_slide)
        slider.set(self.font_size)
        slider.pack(fill="x", pady=(0, 6))

        # Min/Max labels under slider
        range_row = ctk.CTkFrame(body, fg_color="transparent")
        range_row.pack(fill="x", pady=(0, 18))
        ctk.CTkLabel(range_row, text="Smaller", font=ctk.CTkFont(size=10),
                     text_color="#444").pack(side="left")
        ctk.CTkLabel(range_row, text="Larger", font=ctk.CTkFont(size=10),
                     text_color="#444").pack(side="right")

        # Preview text
        preview = ctk.CTkLabel(
            body,
            text="This is how text will look across the app.",
            font=ctk.CTkFont(size=self.font_size),
            text_color="#ccc", fg_color="#1a1d27",
            corner_radius=8)
        preview.pack(fill="x", ipady=12, pady=(0, 18))

        # Preset buttons
        preset_row = ctk.CTkFrame(body, fg_color="transparent")
        preset_row.pack(fill="x")
        ctk.CTkLabel(preset_row, text="Presets:",
                     font=ctk.CTkFont(size=fs(11)), text_color="#555"
                     ).pack(side="left", padx=(0, 12))
        for label, size in [("Small", 11), ("Default", 14), ("Large", 17), ("X-Large", 22)]:
            ctk.CTkButton(
                preset_row, text=label, width=84, height=30,
                fg_color="#1a1f2e", text_color="#bbb",
                hover_color="#2a3340", corner_radius=8,
                font=ctk.CTkFont(size=fs(11)),
                command=lambda s=size: [slider.set(s), on_slide(s)]
            ).pack(side="left", padx=4)

        # Apply button
        ctk.CTkButton(
            scroll,
            text="Apply & Reload Current Page",
            fg_color="#4dd9c0", hover_color="#3bbfaa",
            text_color="#0f1117", height=48,
            font=ctk.CTkFont(size=fs(13), weight="bold"),
            command=lambda: self.show_page(
                getattr(self, "_last_page", "Log Workout"))
        ).pack(fill="x", pady=(8, 0))

        # ── About card ────────────────────────────────────────────
        about = ctk.CTkFrame(scroll, fg_color="#13151f",
                             border_color="#2a3340", border_width=1, corner_radius=14)
        about.pack(fill="x", pady=(20, 0))

        hdr2 = ctk.CTkFrame(about, fg_color="transparent")
        hdr2.pack(fill="x", padx=22, pady=(18, 6))
        ctk.CTkLabel(hdr2, text="ℹ", font=ctk.CTkFont(size=fs(15)),
                     text_color="#4dd9c0").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(hdr2, text="About AVANCE",
                     font=ctk.CTkFont(size=fs(14), weight="bold"),
                     text_color="#e5e5e5").pack(side="left")
        ctk.CTkFrame(about, fg_color="#2a2d3a", height=1).pack(fill="x", padx=22)

        about_body = ctk.CTkFrame(about, fg_color="transparent")
        about_body.pack(fill="x", padx=22, pady=(14, 20))

        for label, value in [
            ("Version",       "1.0.0  —  Student Project"),
            ("Purpose",       "Track workouts with music to understand your best performance"),
            ("Data storage",  "All data saved locally on your device only"),
            ("Privacy",       "No personal data is collected or shared externally"),
            ("Font",          "Place Audiowide-Regular.ttf in the app folder for branded text"),
        ]:
            r = ctk.CTkFrame(about_body, fg_color="transparent")
            r.pack(fill="x", pady=6)
            ctk.CTkLabel(r, text=label,
                         font=ctk.CTkFont(size=fs(11), weight="bold"),
                         text_color="#7a7f9a", width=110, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=value,
                         font=ctk.CTkFont(size=fs(11)),
                         text_color="#aaa", anchor="w", wraplength=500).pack(side="left")



    # ========== HISTORY PAGE ==========
    def show_history(self):
        """History page with better layout"""
        self.clear_main_frame()
        
        # Title Section
        title = ctk.CTkLabel(
            self.main_frame,
            text="Session History",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#e0e0e0"
        )
        title.pack(anchor="w", padx=30, pady=(20, 5))
        
        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="ALL LOGGED SESSIONS",
            font=ctk.CTkFont(size=10),
            text_color="#555"
        )
        subtitle.pack(anchor="w", padx=30, pady=(0, 20))
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(script_dir, "workout_data.csv")
        
        if not os.path.exists(csv_file):
            no_data = ctk.CTkLabel(
                self.main_frame,
                text="No sessions logged yet.\nGo to 'Log Workout' to add your first session!",
                font=ctk.CTkFont(size=14),
                text_color="#888"
            )
            no_data.pack(pady=100)
            return
        
        df = pd.read_csv(csv_file)
        
        # Top bar with count and clear button
        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(0, 15))
        
        count_label = ctk.CTkLabel(
            top_bar,
            text=f"Total Sessions: {len(df)}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4dd9c0"
        )
        count_label.pack(side="left")
        
        clear_all_btn = ctk.CTkButton(
            top_bar,
            text="🗑️ Clear All Data",
            fg_color="transparent",
            border_color="#d9944d",
            border_width=1,
            hover_color="#d9944d20",
            text_color="#d9944d",
            height=38,
            font=ctk.CTkFont(size=12),
            command=self.clear_all_data
        )
        clear_all_btn.pack(side="right")
        
        # Scrollable table frame
        table_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="#0f1117",
            scrollbar_button_color="#2a2d3a",
            scrollbar_button_hover_color="#4dd9c0"
        )
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Table header - REDUCED WIDTHS
        header_frame = ctk.CTkFrame(table_frame, fg_color="#13151f", corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["Date", "Type", "Mins", "Quality", "Playlist", "Genre", "Artist", "Song", ""]
        header_widths = [75, 70, 50, 65, 95, 70, 85, 100, 50]  # Reduced by ~20%
        
        header_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_container.pack(fill="x", padx=12, pady=10)
        
        for i, (header, width) in enumerate(zip(headers, header_widths)):
            label = ctk.CTkLabel(
                header_container,
                text=header,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#888",
                width=width,
                anchor="w"
            )
            label.pack(side="left", padx=3)
        
        # Data rows - REDUCED WIDTHS
        for index, row in df.iloc[::-1].iterrows():
            row_frame = ctk.CTkFrame(table_frame, fg_color="#1a1d27", corner_radius=8)
            row_frame.pack(fill="x", pady=3)
            
            row_container = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_container.pack(fill="x", padx=12, pady=10)
            
            # Date (shortened to MM-DD)
            date_str = str(row['Date'])
            date_display = date_str[5:10] if len(date_str) >= 10 else date_str[:8]
            date_label = ctk.CTkLabel(
                row_container,
                text=date_display,
                font=ctk.CTkFont(size=11),
                text_color="#e0e0e0",
                width=75,
                anchor="w"
            )
            date_label.pack(side="left", padx=3)
            
            # Workout Type (shortened)
            workout_label = ctk.CTkLabel(
                row_container,
                text=str(row['Workout_Type'])[:8],
                font=ctk.CTkFont(size=11),
                text_color="#e0e0e0",
                width=70,
                anchor="w"
            )
            workout_label.pack(side="left", padx=3)
            
            # Duration (just number)
            duration_label = ctk.CTkLabel(
                row_container,
                text=str(row['Duration']),
                font=ctk.CTkFont(size=11),
                text_color="#e0e0e0",
                width=50,
                anchor="w"
            )
            duration_label.pack(side="left", padx=3)
            
            # Performance with color
            perf_str = str(row['Performance'])
            perf_value = int(perf_str.split('/')[0]) if '/' in perf_str else int(perf_str) if perf_str.isdigit() else 0
            perf_color = "#4dd9c0" if perf_value >= 7 else "#d9944d" if perf_value >= 5 else "#888"
            
            perf_label = ctk.CTkLabel(
                row_container,
                text=f"{perf_value}/10",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=perf_color,
                width=65,
                anchor="w"
            )
            perf_label.pack(side="left", padx=3)
            
            # Playlist (shortened)
            playlist_label = ctk.CTkLabel(
                row_container,
                text=str(row['Playlist'])[:12],
                font=ctk.CTkFont(size=11),
                text_color="#e0e0e0",
                width=95,
                anchor="w"
            )
            playlist_label.pack(side="left", padx=3)
            
            # Genre (shortened)
            genre_label = ctk.CTkLabel(
                row_container,
                text=str(row['Genre'])[:9],
                font=ctk.CTkFont(size=11),
                text_color="#e0e0e0",
                width=70,
                anchor="w"
            )
            genre_label.pack(side="left", padx=3)
            
            # Artist (shortened)
            artist_label = ctk.CTkLabel(
                row_container,
                text=str(row['Artist'])[:11],
                font=ctk.CTkFont(size=11),
                text_color="#e0e0e0",
                width=85,
                anchor="w"
            )
            artist_label.pack(side="left", padx=3)
            
            # Song (shortened)
            song_label = ctk.CTkLabel(
                row_container,
                text=str(row['Fav_Song'])[:13] if pd.notna(row['Fav_Song']) else "-",
                font=ctk.CTkFont(size=11),
                text_color="#e0e0e0",
                width=100,
                anchor="w"
            )
            song_label.pack(side="left", padx=3)
            
            # Delete button (smaller)
            delete_btn = ctk.CTkButton(
                row_container,
                text="✕",
                fg_color="transparent",
                hover_color="#d9944d30",
                text_color="#d9944d",
                width=50,
                height=28,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda idx=index: self.confirm_delete_session(idx)
            )
            delete_btn.pack(side="left", padx=3)
    
    def confirm_delete_session(self, row_index):
        """Confirmation popup"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("380x180")
        dialog.configure(fg_color="#1a1d27")
        dialog.transient(self)
        dialog.grab_set()
        
        warning = ctk.CTkLabel(
            dialog,
            text="Delete This Session?",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#d9944d"
        )
        warning.pack(pady=(25, 10))
        
        message = ctk.CTkLabel(
            dialog,
            text="This action cannot be undone.",
            font=ctk.CTkFont(size=11),
            text_color="#888"
        )
        message.pack(pady=(0, 25))
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="transparent",
            border_color="#2a2d3a",
            border_width=1,
            hover_color="#1e2130",
            text_color="#888",
            width=100,
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=5)
        
        def do_delete():
            dialog.destroy()
            self.delete_session(row_index)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            fg_color="#d9944d",
            hover_color="#b87a3d",
            text_color="#0f1117",
            width=100,
            command=do_delete
        )
        delete_btn.pack(side="left", padx=5)
    
    def delete_session(self, row_index):
        """Delete single session"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(script_dir, "workout_data.csv")
        
        df = pd.read_csv(csv_file)
        df = df.drop(row_index)
        df.to_csv(csv_file, index=False)
        
        print(f"✅ Session deleted!")
        self.show_history()
    
    def clear_all_data(self):
        """Clear all sessions"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("400x200")
        dialog.configure(fg_color="#1a1d27")
        dialog.transient(self)
        dialog.grab_set()
        
        warning = ctk.CTkLabel(
            dialog,
            text="⚠️ Delete All Sessions?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#d9944d"
        )
        warning.pack(pady=(30, 10))
        
        message = ctk.CTkLabel(
            dialog,
            text="This will permanently delete all your workout data.\nThis action cannot be undone!",
            font=ctk.CTkFont(size=12),
            text_color="#888"
        )
        message.pack(pady=(0, 30))
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="transparent",
            border_color="#2a2d3a",
            border_width=1,
            hover_color="#1e2130",
            text_color="#888",
            width=120,
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=5)
        
        def confirm_delete():
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_file = os.path.join(script_dir, "workout_data.csv")
            
            if os.path.exists(csv_file):
                os.remove(csv_file)
                print("🗑️ All data cleared!")
            
            dialog.destroy()
            self.show_history()
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete All",
            fg_color="#d9944d",
            hover_color="#b87a3d",
            text_color="#0f1117",
            width=120,
            command=confirm_delete
        )
        delete_btn.pack(side="left", padx=5)

# ========== SPLASH SCREEN ==========
class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent, on_done):
        super().__init__(parent)
        self.on_done = on_done
        self.overrideredirect(True)

        w, h = 500, 320
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.configure(fg_color="#0f1117")
        self.lift()
        self.attributes("-topmost", True)

        ctk.CTkLabel(
            self, text="AVANCE",
            font=audiowide_font(52),
            text_color="#4dd9c0"
        ).pack(pady=(60, 4))

        ctk.CTkLabel(
            self, text="FITNESS . WORKOUT",
            font=ctk.CTkFont(size=12),
            text_color="#555"
        ).pack()

        ctk.CTkLabel(
            self, text="Track your workouts. Feel your music.",
            font=ctk.CTkFont(size=13),
            text_color="#888"
        ).pack(pady=(18, 30))

        self.progress = ctk.CTkProgressBar(self, width=280, height=5,
                                            fg_color="#1e2130",
                                            progress_color="#4dd9c0")
        self.progress.pack()
        self.progress.set(0)

        self._step = 0
        self._animate()

    def _animate(self):
        self._step += 1
        self.progress.set(self._step / 30)
        if self._step < 30:
            self.after(40, self._animate)
        else:
            self.after(200, self._finish)

    def _finish(self):
        self.destroy()
        self.on_done()


# ========== ONBOARDING SCREEN ==========
class OnboardingScreen(ctk.CTkToplevel):
    SLIDES = [
        {
            "icon":  "🏋️",
            "title": "Welcome to AVANCE",
            "body":  "AVANCE combines your workouts and your music into one place. Every session you log helps you understand what drives your best performance.",
        },
        {
            "icon":  "🎵",
            "title": "Log Your Workout",
            "body":  "Fill in each field to record your session — artist, playlist, duration, performance, and more. You can also download the Excel template to log multiple sessions at once, then upload the file.",
        },
        {
            "icon":  "📊",
            "title": "Track Your Progress",
            "body":  "Your Dashboard shows your streak, session history, and performance over time — so you can see exactly how consistent you have been.",
        },
        {
            "icon":  "🔍",
            "title": "Discover Your Insights",
            "body":  "The Insights page analyses your sessions to show which artists, playlists, and genres push your performance the highest — and recommends new music to match.",
        },
    ]

    def __init__(self, parent, on_done):
        super().__init__(parent)
        self.on_done = on_done
        self.current = 0

        self.overrideredirect(True)
        w, h = 560, 420
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.configure(fg_color="#0f1117")
        self.lift()
        self.attributes("-topmost", True)

        # Header bar
        header = ctk.CTkFrame(self, fg_color="#13151f", height=56, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="AVANCE",
                     font=audiowide_font(16),
                     text_color="#4dd9c0").pack(side="left", padx=24, pady=14)
        ctk.CTkLabel(header, text="FITNESS . WORKOUT",
                     font=ctk.CTkFont(size=9), text_color="#555").pack(side="left")

        # Slide content area
        self.content = ctk.CTkFrame(self, fg_color="#0f1117")
        self.content.pack(fill="both", expand=True, padx=40, pady=10)

        self.icon_lbl  = ctk.CTkLabel(self.content, text="", font=ctk.CTkFont(size=48))
        self.icon_lbl.pack(pady=(20, 8))

        self.title_lbl = ctk.CTkLabel(self.content, text="",
                                       font=ctk.CTkFont(size=20, weight="bold"),
                                       text_color="#e5e5e5")
        self.title_lbl.pack()

        self.body_lbl = ctk.CTkLabel(self.content, text="",
                                      font=ctk.CTkFont(size=13),
                                      text_color="#888",
                                      wraplength=440,
                                      justify="center")
        self.body_lbl.pack(pady=(14, 0))

        # Dot indicators
        self.dots_frame = ctk.CTkFrame(self, fg_color="#0f1117")
        self.dots_frame.pack(pady=(0, 10))
        self.dots = []
        for i in range(len(self.SLIDES)):
            d = ctk.CTkLabel(self.dots_frame, text="●",
                              font=ctk.CTkFont(size=10),
                              text_color="#555")
            d.pack(side="left", padx=4)
            self.dots.append(d)

        # Bottom buttons
        btn_row = ctk.CTkFrame(self, fg_color="#0f1117")
        btn_row.pack(fill="x", padx=40, pady=(0, 24))

        self.skip_btn = ctk.CTkButton(
            btn_row, text="Skip",
            fg_color="transparent", text_color="#555",
            hover_color="#1a1a2e", width=80,
            command=self._finish)
        self.skip_btn.pack(side="left")

        self.next_btn = ctk.CTkButton(
            btn_row, text="Next →",
            fg_color="#4dd9c0", text_color="#0f1117",
            hover_color="#3bbfaa", width=120,
            font=ctk.CTkFont(weight="bold"),
            command=self._next)
        self.next_btn.pack(side="right")

        self._show_slide(0)

    def _show_slide(self, idx):
        slide = self.SLIDES[idx]
        self.icon_lbl.configure(text=slide["icon"])
        self.title_lbl.configure(text=slide["title"])
        self.body_lbl.configure(text=slide["body"])
        for i, d in enumerate(self.dots):
            d.configure(text_color="#4dd9c0" if i == idx else "#333")
        is_last = idx == len(self.SLIDES) - 1
        self.next_btn.configure(text="Get Started" if is_last else "Next →")
        self.skip_btn.configure(text="" if is_last else "Skip")

    def _next(self):
        if self.current < len(self.SLIDES) - 1:
            self.current += 1
            self._show_slide(self.current)
        else:
            self._finish()

    def _finish(self):
        self.destroy()
        self.on_done()


# ========== LAUNCH LOGIC ==========
FIRST_LAUNCH_FLAG = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".avance_launched")

def launch():
    root = ctk.CTk()
    root.withdraw()  # hide main window until ready

    first_time = not os.path.exists(FIRST_LAUNCH_FLAG)

    def open_main():
        # Write flag so onboarding won't show again
        if first_time:
            with open(FIRST_LAUNCH_FLAG, "w") as f:
                f.write("launched")
        root.deiconify()
        app = AvanceApp()
        app.mainloop()

    def after_splash():
        if first_time:
            OnboardingScreen(root, on_done=open_main)
        else:
            open_main()

    splash = SplashScreen(root, on_done=after_splash)
    root.mainloop()


if __name__ == "__main__":
    launch()