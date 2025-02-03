# BharatFD Backend Intern Assignment

## Name: Rohan Gudimetla

## Email: rohan.gudimetla07@gmail.com

<details>
  <summary><strong>Backend Intern Assignment Details</strong></summary>
Hiring Test for Backend Developers
NOTE : You can use NodeJs/Python/ (Django/ExpressJS or any other framework of your choice as well)
Objective
The objective of this test is to evaluate the candidate’s ability to:

Design and implement Django models with WYSIWYG editor support.
Store and manage FAQs with multi-language translation.
Follow PEP8 conventions and best practices.
Write a clear and detailed README.
Use proper Git commit messages.
Task Requirements

1. Model Design
   Create a model to store FAQs.
   Each FAQ should have:
   A question (TextField)
   An answer (RichTextField for WYSIWYG editor support)
   Language-specific translations (question_hi, question_bn, etc.).
   Implement a model method to retrieve translated text dynamically.
2. WYSIWYG Editor Integration
   Use django-ckeditor to allow users to format answers properly.
   Ensure that the WYSIWYG editor supports multilingual content.
3. API Development
   Create a ** REST API** for managing FAQs.
   Support language selection via ?lang= query parameter.
   Ensure responses are fast and efficient using pre-translation.
4. Caching Mechanism
   Implement ** cache framework** to store translations.
   Use Redis for improved performance.
5. Multi-language Translation Support
   Use Google Translate API or googletrans.
   Automate translations during object creation.
   Provide fallback to English if translation is unavailable.
6. Admin Panel
   Register the FAQ model in the Admin site or create one seperately.
   Enable a user-friendly admin interface for managing FAQs.
7. Unit Tests & Code Quality
   Write unit tests using pytest or mocha/chai.
   Ensure tests cover model methods and API responses.
   Follow PEP8/ES6 guidelines and use flake8/JS tools for linting.
8. Documentation
   Write a detailed README with:
   Installation steps
   API usage examples
   Contribution guidelines
   Ensure the README is well-structured and easy to follow.
9. Git & Version Control
   Use Git for version control.
   Follow conventional commit messages:
   feat: Add multilingual FAQ model
   fix: Improve translation caching
   docs: Update README with API examples
   Ensure atomic commits with clear commit messages.
10. Deployment & Docker Support (Bonus)
    Provide a Dockerfile and docker-compose.yml.
    Deploy the application to Heroku or AWS (optional).

</details>

## Tech Stack

- **Language**: Python
- **Framework**: Django
- **Database**: PostgreSQL
- **Caching**: Redis
- **Formatting**: Black
- **API Documentation**: Swagger UI
- **googletrans**: To translate the FAQs into various supported languages.
- **django-ckeditor**: To provide a WYSIWYG editor for FAQs answers, supporting multiple languages.

## Deployment

- The APIs can be tested using `Swagger` UI deployed at https://bharatfd-app-1.onrender.com/docs
- The API requests are served at https://bharatfd-app-1.onrender.com/
- The APIs described in the later `API Usage` section can be implemented on this server!
- The Admin Panel can be accessed at https://bharatfd-app-1.onrender.com/admin (username - `roanster007`, password - `password`)

## How to setup and run locally (With Docker)

1. **Clone the repository:**

```bash
   git clone git@github.com:roanster007/bharatfd.git
```

2. **Rename `.env.dev` to `.env`**

3. **Build the docker image:**

```bash
   docker-compose build
```

This will install all the requirements, and build the Docker image.

4. **Run the Docker container**:

```bash
docker-compose up
```

This will spin up the server. The API is accessible at `localhost:8000`.

5. **Admin Panel**:

To access the admin panel, run:

```bash
./manage.py createsuperuser
```

Then set the username, password, after which the admin panel is accessible at `localhost:8000/admin`.

## Troubleshooting

Sometimes in Windows systems, the locally running postgres instance might be interrupting with that
in the docker container. To fix this:

1. **Open Postgres shell**

```bash
sudo -u postgres psql
```

2. **Create Database**

```bash
CREATE DATABASE bharatfd;
```

3. **Create User**

```bash
CREATE USER bharatfd WITH PASSWORD 'password';
```

4. **Grant Permissions**

```bash
GRANT ALL PRIVILEGES ON DATABASE bharatfd TO bharatfd;
```

## API Usage

- The REST API documentation of each field / method is described in detailed at `faqs/faqs.yaml` as per OpenAPI format.
- The API documentation can be tested locally at `localhost:8000/docs`, where API docs is rendered using `SWAGGER UI`. After starting the server, the APIs can be tested there, without the need of any `curl` on terminal requests or `POSTMAN`.

### API Endpoints:

- The API endpoint for accessing and managing FAQs is `/faqs`.
- The methods available are:

1. **GET**:

- returns a list of Json objects of FAQs, where each object contains FAQ ID, Question, Answer and Language.
- It requires an additional language parameter, in `ISO 639-1` format (`en` for English, `hi` for Hindi, etc.)
  The currently Supported languages are Hindi, English, Bengali, Japanese, Italian and German. The languages available can be seen at `faqs/models.py` at `Language` class.
- Based on the language parameter, all the FAQs are fetched in that particular language.
- If no language is provided, it is defaulted to `en`.

Example Request:

```bash
curl -X GET "http://localhost:8000/faqs?lang=hi"
```

Response:

```bash
{
  "faqs": [
    {
      "id": 17,
      "language": "Hindi",
      "question": "क्या आप अभी भी हैं",
      "answer": "<p>क्या आप अभी भी हैं</p>"
    },
  ]
}
```

If language provided is not supported, it returns:

```bash
{
    "error": "Language not supported!"
}
```

2. **POST**:

- Allows adding of an FAQ Question and Answer.
- Takes two parameters - Question and Answer
- It then automatically pre-translates the Question and Answer into supported languages using the `googletrans` library and stores them.

Example Request:

```bash
curl -X POST "http://localhost:8000/faqs?question=How%20are%20you&answer=I%20am%20good"
```

Response:

```bash
{
    "success": "Successfully created new FAQ entry!"
}
```

If any entry missed:

```bash
{
    "error": "Missing FAQ question or answer!"
}
```

3. **DELETE**:

- Delete a particular FAQ using its ID.

Example Request:

```bash
curl -X DELETE "http://localhost:8000/faqs?id=17"
```

Response:

```bash
{
    "success": "Successfully deleted FAQ entry!"
}
```

If ID entry missed:

```bash
{
    "error": "FAQ ID not mentioned"
}
```

If ID is not integer:

```bash
{
    "error": "ID parameter must be an integer."
}
```

## Caching

- All the FAQs in English Language are cached using Redis, and continuously maintained, since it might be one of the most used languages to access FAQs across the app.
- Support for additional common languages might be added to be CACHED, so as to reduce Latency for queries.

## Model Design

- This app stores FAQs using two models:

1. FAQ
2. FAQTranslation

An additional TextChoices model - `Language` handles all the supported languages in our app.

- Each FAQ created by user is first stored in the FAQ model, along with the base or the actual language name that FAQ is based on.
- Once the FAQ is stored there, then `googletrans` library is used to convert the question and answer to each of the supported languages mentioned in `Language`, and stores the translated question and answer, along with the language translated to, and a `ForeignKey` reference to the original FAQ instance created.

- This type of design **prevents frequent schema change** requirement, when we start expanding our language base, and add many newer languages.
- To display FAQs in a particular language, we just Filter rows from `FAQTranslation` model, with that language field.

## Contributing Guidelines

- New Features or Optimizations are Welcome!
- Please clone the repository, and set up the environment as described above.
- Make proper changes, and add necessary tests which validate the behaviour
- Once you make your changes, make sure you format them using `black` formatter!
- Please follow commit discipline -- make sure each commit is of format -- `changes_made: Short summary`.
- Verify your changes by rebuilding the docker image and spinning it up.
- Open a Pull Request with necessary changes, and tag the core maintainers for a review!
