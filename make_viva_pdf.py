from fpdf import FPDF

class VivaGuidePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(59, 130, 246)
        self.cell(0, 10, 'AI Smart City - Viva & Hackathon Study Guide', 0, 1, 'C')
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(17, 24, 39)
        self.set_fill_color(243, 244, 246)
        self.cell(0, 10, title, 0, 1, 'L', fill=True)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Helvetica', '', 12)
        self.set_text_color(55, 65, 81)
        # Using multi_cell for automatic line breaking
        self.multi_cell(0, 7, text)
        self.ln(6)
        
    def sub_heading(self, text):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(31, 41, 55)
        self.cell(0, 8, text, 0, 1, 'L')
        self.ln(2)

    def bullet(self, text):
        self.set_font('Helvetica', '', 12)
        self.set_text_color(55, 65, 81)
        self.multi_cell(0, 7, f"-  {text}")
        self.ln(2)

def create_viva_pdf():
    pdf = VivaGuidePDF()
    pdf.add_page()
    
    # 1. ARCHITECTURE
    pdf.chapter_title("1. System Architecture & Tech Stack")
    pdf.chapter_body(
        "The project is structured using the Flask 'Blueprint' pattern. This means the backend isn't just one huge file, "
        "but separated into logical modules like traffic.py, waste.py, complaints.py, etc. This is a crucial point for the Viva: "
        "it shows you understand modular architecture and separation of concerns.\n\n"
        "Tech Stack Details:\n"
        "- Backend: Python, Flask (lightweight, perfect for fast hackathons).\n"
        "- Database: SQLite via SQLAlchemy ORM (Object Relational Mapping). We used SQLite because it requires zero configuration, "
        "which is ideal for hackathon demos. For production, you'd mention migrating to PostgreSQL.\n"
        "- Frontend: Vanilla JS, HTML, CSS. Leaflet.js used for rendering the open-source map.\n"
        "- Real-time Data: We used APScheduler to run a background Python job that constantly injects simulated IoT sensor data into the database."
    )

    # 2. MACHINE LEARNING DEEP DIVE
    pdf.chapter_title("2. Machine Learning Models (Crucial for Judge Q&A)")
    
    pdf.sub_heading("A. Traffic Congestion Prediction")
    pdf.bullet("Algorithm: RandomForestRegressor (Scikit-Learn).")
    pdf.bullet("Inputs/Features: Vehicle count, average speed, current congestion level.")
    pdf.bullet("Target: Predicts the congestion level 30 minutes into the future.")
    pdf.bullet("Why Random Forest?: Traffic isn't strictly linear. Speed drops rapidly once a road hits a certain capacity. Trees capture these non-linear thresholds better than simple linear models.")
    pdf.bullet("Fallback Mechanism: If the DB has < 30 rows of data (like at the start of the app), the model falls back to a clever heuristic (mean reversion) rather than crashing.")

    pdf.sub_heading("B. Waste Bin Fill Prediction")
    pdf.bullet("Algorithm: LinearRegression (Scikit-Learn).")
    pdf.bullet("Inputs/Features: Time (index of the last 24 readings).")
    pdf.bullet("Target: Predicts fill percentage 5 hours ahead.")
    pdf.bullet("Why Linear?: Trash accumulation over a few hours is generally a steady, linear trend. Overcomplicating it with deep learning would lead to overfitting.")

    # 3. FRONTEND & DOM
    pdf.chapter_title("3. Frontend Mechanics & The JS Refactor")
    pdf.chapter_body(
        "Initially, the frontend JavaScript was a massive monolith (app.js). We refactored it into feature-specific files "
        "(traffic.js, waste.js, environment.js, etc.).\n\n"
        "How data updates: The frontend uses `setInterval` to 'poll' the backend /api/ endpoints every 6 seconds using the Fetch API. "
        "We use `Promise.all` to fetch multiple endpoints concurrently, which speeds up the dashboard loading time significantly."
    )

    # 4. POTENTIAL VIVA QUESTIONS & ANSWERS
    pdf.chapter_title("4. Potential Viva / Judge Questions & Answers")
    
    pdf.sub_heading("Q: How does your system get 'Live' data?")
    pdf.chapter_body("A: In a real city, we would have IoT sensors (cameras, bin weight sensors). For this hackathon, we built a custom Python Simulator using APScheduler that generates realistic telemetry and writes it to our database every few seconds.")

    pdf.sub_heading("Q: Why did you use HTTP Polling instead of WebSockets?")
    pdf.chapter_body("A: HTTP polling (fetching data every X seconds) was chosen for speed of development and simplicity during the hackathon. It works well for dashboards. If asked how to scale it, say: 'In production, we would upgrade to WebSockets (e.g., Socket.IO) to push data from server to client instantly, reducing HTTP overhead.'")

    pdf.sub_heading("Q: What if the AI model receives bad data?")
    pdf.chapter_body("A: We implemented boundaries and fallbacks. For example, the traffic model checks if there are enough rows to train. The prediction outputs are clamped between 0% and 100% using max/min functions so the UI never breaks.")

    # 5. HACKATHON LEARNINGS
    pdf.add_page() # Move to next page for neatness
    pdf.chapter_title("5. Ultimate Hackathon Learnings (For the Future)")
    pdf.bullet("Modularization Saves Lives: Lumping all code into app.py or app.js leads to nightmare merge conflicts and bugs. Segregating code early into 'features' makes debugging 10x faster.")
    pdf.bullet("Handle Nulls Gracefully: Always wrap DOM element selections (document.getElementById) in an 'if' check. If an element is missing on a specific HTML page, an unhandled null exception will crash the entire script.")
    pdf.bullet("AI is more than just API Calls: Training simple Scikit-Learn models on-the-fly gives you complete control and is much faster/cheaper than hitting external LLMs for numerical forecasting.")
    pdf.bullet("UI/UX Matters: Judges love dark mode, clean CSS variables, and interactive elements (like the Leaflet map tooltips). It makes the project feel finished.")

    pdf.output("Viva_Study_Guide.pdf")

create_viva_pdf()
