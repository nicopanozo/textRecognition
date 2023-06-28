from flask import Flask, render_template, request, url_for
import os
from PIL import Image
import pytesseract
import matplotlib.pyplot as plt
import numpy as np
from googletrans import Translator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded images

# Google Translate API configuration
translator = Translator(service_urls=['translate.google.com'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    # Get the uploaded image file
    file = request.files['image']

    # Save the file to the upload folder
    filename = file.filename

    # With this line, you can recognize images in .jpeg and .jpg formats
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # With this code, you can recognize various images in different formats
    file_extension = os.path.splitext(filename)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']  # Add the formats you want to support

    if file_extension in allowed_extensions:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        return "Unsupported image format"

    # Process the image and extract the text using pytesseract
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)

    # Count the number of text lines
    lines_count = len(text.split('\n'))

    # Get the most used words
    words = text.split()
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Change the backend of Matplotlib to generate the plots in the main thread
    plt.switch_backend('agg')

    # generamos histograma o grafico de barras con las frecuencias de cada palabra
    plt.figure(figsize=(8, 6))
    plt.bar(range(len(top_words)), [count for _, count in top_words], align='center')
    plt.xticks(range(len(top_words)), [word for word, _ in top_words], rotation='vertical')
    plt.xlabel('Word')
    plt.ylabel('Frequency')
    plt.title('Chart of Most Used Words')
    plt.tight_layout()
    plt.savefig('static/word_chart.png')
    plt.close()

    # generamos un grafico de dispersion de las word frequencies
    plt.figure(figsize=(8, 6))
    plt.scatter(range(len(top_words)), [count for _, count in top_words])
    plt.xlabel('Word')
    plt.ylabel('Frequency')
    plt.title('Scatter Plot of Word Frequencies')
    plt.xticks(range(len(top_words)), [word for word, _ in top_words], rotation='vertical')
    plt.tight_layout()
    plt.savefig('static/scatter_plot.png')
    plt.close()

    # generamos un grafico de torta de las palabras más usadas
    plt.figure(figsize=(8, 6))
    labels = [word for word, _ in top_words]
    sizes = [count for _, count in top_words]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Distribution of Most Used Words')
    plt.tight_layout()
    plt.savefig('static/pie_chart.png')
    plt.close()

    # generamos una gráfica de radar de las palabras más usadas
    categories = [word for word, _ in top_words]
    frequencies = [count for _, count in top_words]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    frequencies += frequencies[:1]

    plt.figure(figsize=(8, 6))
    plt.polar(angles, frequencies, marker='o')
    plt.fill(angles, frequencies, alpha=0.25)
    plt.xticks(angles[:-1], categories)
    plt.title('Frequency of Most Used Words')
    plt.tight_layout()
    plt.savefig('static/radar_chart.png')
    plt.close()

    return render_template('result.html', text=text, lines_count=lines_count, words=words, top_words=top_words)


@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['text']
    if not text:
        error_message = "No text recognized for translation."
        return render_template('translate.html', text=text, error_message=error_message)
    try:
        translation_es = translate_text(text, 'es', 'en')  # Translate from Spanish to English
        translation_en = translate_text(text, 'en', 'es')  # Translate from English to Spanish
        return render_template('translate.html', text=text, translation_es=translation_es, translation_en=translation_en)
    except:
        error_message = "An error occurred while performing the translation."
        return render_template('translate.html', text=text, error_message=error_message)

def translate_text(text, source_lang, target_lang):
    try:
        translation = translator.translate(text, src=source_lang, dest=target_lang).text
        return translation
    except Exception as e:
        error_message = str(e)
        return None

if __name__ == '__main__':
    app.run(port=5000)
