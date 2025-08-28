# Inventory Management API: An AI-Powered REST Service

A robust REST API for inventory management, built with Spring Boot. This project features secure, validated endpoints, a relational database schema, high-performance caching, and an advanced AI-powered query engine. The entire application is containerized and includes a complete CI/CD pipeline with automated integration testing for production readiness.

## Key Features

* **AI-Powered Queries**: An endpoint that securely translates natural language questions (e.g., "how many laptops are in stock?") into executable SQL queries using an external LLM.
* **Relational Database Schema**: Uses PostgreSQL with JPA/Hibernate for object-relational mapping between `Product` and `Supplier` entities.
* **Database Migrations**: Leverages Flyway for version-controlled, automated database schema changes, ensuring consistency across all environments.
* **High-Performance Caching**: Integrates Redis to cache database query results, significantly reducing latency on frequent requests.
* **Robust API Validation**: Employs Jakarta Bean Validation to automatically validate incoming data, preventing invalid entries from reaching the business logic.
* **Automated Testing**: A comprehensive test suite using **JUnit** and **Mockito** for unit tests, and **Testcontainers** for reliable, self-contained integration tests.
* **CI/CD Pipeline**: A GitHub Actions workflow automatically builds and runs the full test suite on every push.
* **Containerized Environment**: The entire application is containerized with Docker, ensuring portability and consistent deployments.

## Tech Stack

| Category         | Technology                                                                     |
| ---------------- | ------------------------------------------------------------------------------ |
| **Backend** | Java 17, Spring Boot, Spring Data JPA, Hibernate, Spring WebFlux (for WebClient) |
| **Database** | PostgreSQL, Redis, Flyway                                                      |
| **DevOps** | Docker, Docker Compose, GitHub Actions                                         |
| **Testing** | JUnit 5, Mockito, Testcontainers                                               |
| **AI** | Groq API (or other LLM APIs)                                                   |

## System Architecture

The application runs as a multi-container stack orchestrated by Docker Compose for local development. The Spring Boot application serves the API, connecting to PostgreSQL for persistence and Redis for caching. For the AI query feature, it communicates externally with an LLM API.

`User/Client (Postman) -> Spring Boot API -> (1. AIService -> LLM API), (2. Repository/JdbcTemplate -> Redis Cache / PostgreSQL DB)`

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

* Java Development Kit (JDK) 17+
* Docker and Docker Compose
* A Groq API Key (or other LLM provider key)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [link to this repository]
    cd inventory-api
    ```

2.  **Create an environment file:**
    Create a file named `.env` in the root directory and add your API key:
    ```
    GROQ_API_KEY=your_secret_api_key_goes_here
    ```

3.  **Add `docker-compose.yml`:**
    Create a file named `docker-compose.yml` in the root directory with the following content. This will manage the PostgreSQL and Redis services for you.

    <details>
    <summary>Click to expand docker-compose.yml</summary>

    ```yaml
    version: '3.8'
    services:
      postgres:
        image: postgres:15-alpine
        container_name: inventory-postgres
        ports:
          - "5432:5432"
        environment:
          - POSTGRES_USER=inventory_user
          - POSTGRES_PASSWORD=password
          - POSTGRES_DB=inventory_db
        volumes:
          - postgres_data:/var/lib/postgresql/data

      redis:
        image: redis:7-alpine
        container_name: inventory-redis
        ports:
          - "6379:6379"
        volumes:
          - redis_data:/data

    volumes:
      postgres_data:
      redis_data:
    ```
    </details>

4.  **Start external services:**
    Run the following command to start PostgreSQL and Redis in the background.
    ```bash
    docker-compose up -d
    ```

5.  **Run the application:**
    Use the Maven wrapper to run the Spring Boot application. It will automatically connect to the services started by Docker Compose.
    ```bash
    ./mvnw spring-boot:run
    ```

The API will now be available at `http://localhost:8080`.

## API Endpoints

| Method | Path                 | Auth
