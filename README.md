# 🎬 Movie Catalog & Recommender System
### Assignment 2 · Cloud & Advanced Analytics (HEC Lausanne)

> A 2-tier movie recommendation application deployed on Google Cloud Run, featuring Elasticsearch autocomplete, personalized ML-based recommendations (BigQuery ML), and rich TMDB metadata.

**🔗 Live App (Frontend) :** [https://streamlit-frontend-848449588029.europe-west6.run.app/](https://streamlit-frontend-848449588029.europe-west6.run.app/)

---

## 🏗️ Architecture & 2-Tier Structure

The project is built using a modern **2-tier architecture**, fully containerized via Docker and deployable on Google Cloud Run.

### 1. Frontend (Streamlit)
- **Role:** Handles the graphical user interface, user input processing, and result visualization.
- **Features:** 
  - Netflix-like premium UI with posters and rich metadata.
  - Interactive **Elasticsearch-powered** search autocomplete.
  - Interface allowing users to select ("Like") multiple preferred movies to generate personalized recommendations.
- **Deployment:** Dockerized and hosted on a dedicated Google Cloud Run service.

### 2. Backend (Flask ML API)
- **Role:** Serves as the central backend API for data processing, recommendation generation, and Elasticsearch proxy.
- **Features:**
  - Connects to **Google BigQuery** to fetch popular movies and identify similar users for the cold-start problem.
  - Connects to **Elasticsearch** to provide sub-second autocomplete suggestions based on the movie index.
  - Fetches real-time movie posters from the **TMDB API**.
- **Deployment:** Dockerized and hosted on a separate Google Cloud Run service.

---

## ✨ Features & Assignment Requirements

### 1. Elasticsearch Autocomplete
- The backend hosts a `/autocomplete` endpoint connected to an Elasticsearch index containing all movies.
- The Streamlit frontend calls this endpoint to provide real-time, fast-as-you-type search suggestions directly beneath the search bar without needing to refresh the page.

### 2. Personalized Recommender System (BigQuery ML)
- A **Matrix Factorization** model was trained using BigQuery ML on the `ml-small-movies` dataset.
- **Cold-Start Problem Handling:** 
  - When a new web user interacts with the app (without an existing userID in the database), they can "Like" multiple movies.
  - The backend receives these IDs and dynamically computes recommendations based on user similarities.
  - If no movie is selected, the application displays a generic list of top popular movies (global recommendations based on highest ratings count).

### 3. User Similarity Computation Method
To address the cold-start problem for web app users, we identify the most similar users dynamically via BigQuery SQL:
1. **Identify High Ratings:** We find users in the dataset (`Ratings_train`) who have given high ratings to the exact same movies the web app user just liked.
2. **Rank by Overlap:** We compute the intersection of preferred movies. Users who share the highest number of highly-rated movies with the current user's selection are ranked highest.
3. **Generate Recommendations:** We select the top-$k$ most similar users and fetch the movies *they* liked and rated highly (but that the current user hasn't seen yet). These movies act as our personalized recommendations.

### 4. Docker & Google Cloud Deployment
- **Docker Compose:** The entire stack (frontend + backend) can be launched and tested locally using `docker compose up --build`.
- **Terminal Execution Logging:** As per the assignment requirements, SQL queries and their outputs (row count and preview) are explicitly logged to the terminal / Cloud Logs for debugging and evaluation.

---

## 🐳 Docker & Deployment

The application is thoroughly containerized, making it easy to run locally or deploy to the cloud.

### 1. Dockerfiles & Containers
The project uses two separate Dockerfiles to maintain a strict 2-tier architecture:
- **`streamlit_app/Dockerfile`**: Configures the Python 3.11 environment for the Streamlit frontend UI.
- **`ML_Backend/Dockerfile`**: Configures the environment for the Flask API serving BigQuery ML recommendations and Elasticsearch endpoints.

### 2. Local Execution (Docker Compose)
You can launch the entire stack on your local machine with a single command. The included `docker-compose.yml` mounts the necessary volumes and maps the ports.

```bash
# Launch the backend API and frontend UI simultaneously
docker compose up --build
```
- **Frontend UI:** `http://localhost:8501`
- **Backend API:** `http://localhost:5001`

### 3. Google Cloud Run Deployment
The application is designed to be hosted serverlessly on **Google Cloud Run**. You can deploy the containers directly from the source code using the Google Cloud CLI.

**Deploying the Streamlit Frontend:**
```bash
gcloud run deploy streamlit-frontend --source . --region europe-west6 --allow-unauthenticated
```
*(Run this command from inside the `streamlit_app` directory)*

**Deploying the ML Backend:**
```bash
gcloud run deploy ml-backend --source . --region europe-west6 --allow-unauthenticated
```
*(Run this command from inside the `ML_Backend` directory)*

---

## 📂 Required Deliverables Check

- [x] **2-Tier Structure:** Backend (Flask) and UI (Streamlit) as separate Docker containers.
- [x] **Elasticsearch:** Used for title autocomplete search bar.
- [x] **BigQuery / BQ ML:** Used for storing datasets and computing the Matrix Factorization recommendation system.
- [x] **Similarity Computation:** Explained in the README.
- [x] **Live URL:** Provided at the top of the README.
- [x] **Terminal Logging:** Executed SQL queries and outputs are logged in the terminal via `bq_service.py`.

---
**Author:** Zakaria Charouite — Cloud & Advanced Analytics 2026