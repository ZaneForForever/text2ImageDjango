

# Django-API-Text-to-Image-and-Sound

Welcome to the Github repository for our advanced multimedia application powered by Django! This application is designed to leverage over 10 different API interfaces along with a locally deployed Stable Diffusion (SD) model to turn text into compelling images. Additionally, we utilize a custom voice model service from Alibaba Cloud to convert text into natural-sounding audio clips.

## Key Features
- **Text-to-Image Generation**: Using a variety of APIs along with a locally hosted Stable Diffusion model, this application can transform your text input into detailed and artistic images.
- **Text-to-Sound Conversion**: With the integration of Alibaba Cloud's custom model service, the application can also convert text to high-quality voice audio, offering a range of voices and languages to choose from.

## Technologies Used
- **Django Framework**: As a high-level Python web framework, Django encourages rapid development and clean, pragmatic design.
- **Stable Diffusion Model**: A cutting-edge model used for realistic image generation from textual descriptions.
- **APIs**: Integration of more than 10 distinct APIs to fetch data and process requests efficiently.
- **Alibaba Cloud Voice Model**: For generating natural and customizable voice audio from text.

## Local Setup
To get this application running locally, follow these steps:
1. **Clone the repository**:
```bash
   git clone https://github.com/yourusername/Django-API-Text-to-Image-and-Sound.git
```

2.  **Install dependencies**:
```bash
    pip install -r requirements.txt
```

3. Run migrations:
```bash
    python manage.py migrate
```
4. Start the server:

```bash
    python manage.py runserver

```


## Usage


To generate images or sound from text, navigate to the respective endpoints via your local server:

**Text to Image**: localhost:8000/ai/text2image/v2
**Text to Sound**: localhost:8000/voice/create
> Feel free to explore the application and utilize its functionalities to convert your creative text inputs into images and sounds!

#### Contributing
Contributions, issues, and feature requests are welcome! Feel free to check Issues page if you want to contribute.

#### License
Distributed under the MIT License. See LICENSE for more information.

#### Contact
For any queries, please open an issue or contact Your Email.

> Enjoy our Django-API-Text-to-Image-and-Sound application and unleash your creativity!