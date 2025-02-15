from flask import Flask, request, jsonify
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

app = Flask(__name__)

# HTML template as a string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crawl4.ai</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background-color: #f8f9fa;
            font-family: 'Montserrat', sans-serif;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        .header h1 {
            font-family: 'Playfair Display', serif;
            font-size: 3rem;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .header p {
            font-size: 1.2rem;
            color: #7f8c8d;
        }
        .input-section {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            text-align: center;
        }
        .url-input {
            width: 70%;
            padding: 1rem;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            margin-right: 1rem;
            transition: border-color 0.3s ease;
        }
        .url-input:focus {
            border-color: #3498db;
            outline: none;
        }
        .crawl-btn {
            padding: 1rem 2rem;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .crawl-btn:hover {
            background-color: #2980b9;
        }
        .loading {
            display: none;
            text-align: center;
            font-size: 1.2rem;
            color: #555;
            margin: 2rem 0;
        }
        .error {
            color: #e74c3c;
            padding: 1rem;
            background-color: #fadbd8;
            border-radius: 8px;
            margin-top: 1rem;
            display: none;
        }
        .results {
            display: none;
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        .section {
            margin-bottom: 3rem;
        }
        .section h2 {
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }
        .links-list, .media-list {
            list-style: none;
            padding: 0;
        }
        .link-item, .media-item {
            padding: 1rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: #fafafa;
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .link-item:hover, .media-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        }
        .link-item a, .media-item a {
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }
        .media-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }
        .media-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 1rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: #fafafa;
        }
        .media-item img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .media-item a {
            font-size: 0.9rem;
            color: #3498db;
            margin-bottom: 0.5rem;
        }
        .media-item strong {
            color: #7f8c8d;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Crawl4.ai</h1>
            <p>Enter a URL to extract links and media</p>
        </div>

        <div class="input-section">
            <input type="url" class="url-input" placeholder="Enter URL (e.g., https://example.com)" required>
            <button class="crawl-btn">Crawl</button>
            <div class="error"></div>
        </div>

        <div class="loading">Crawling the URL...</div>

        <div class="results">
            <div class="section">
                <h2>Internal Links</h2>
                <ul class="links-list" id="internal-links"></ul>
            </div>

            <div class="section">
                <h2>External Links</h2>
                <ul class="links-list" id="external-links"></ul>
            </div>

            <div class="section">
                <h2>Media</h2>
                <div class="media-grid" id="media-items"></div>
            </div>
        </div>
    </div>

    <script>
        $(document).ready(function() {
            $('.crawl-btn').click(function() {
                const url = $('.url-input').val();
                if (!url) {
                    $('.error').text('Please enter a valid URL').show();
                    return;
                }

                $('.loading').show();
                $('.results').hide();
                $('.error').hide();

                $.ajax({
                    url: '/crawl',
                    method: 'POST',
                    data: { url: url },
                    success: function(response) {
                        $('.loading').hide();
                        
                        $('#internal-links').empty();
                        $('#external-links').empty();
                        $('#media-items').empty();

                        response.links.internal.forEach(link => {
                            $('#internal-links').append(`
                                <li class="link-item">
                                    <a href="${link.href}" target="_blank">${link.href}</a><br>
                                    <strong>Text:</strong> ${link.text || 'N/A'}<br>
                                    <strong>Title:</strong> ${link.title || 'N/A'}
                                </li>
                            `);
                        });

                        response.links.external.forEach(link => {
                            $('#external-links').append(`
                                <li class="link-item">
                                    <a href="${link.href}" target="_blank">${link.href}</a><br>
                                    <strong>Text:</strong> ${link.text || 'N/A'}<br>
                                    <strong>Title:</strong> ${link.title || 'N/A'}
                                </li>
                            `);
                        });

                        response.media.images.forEach(img => {
                            $('#media-items').append(`
                                <div class="media-item">
<a href="${img.src}" target="_blank" style="display: inline-block; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${img.src}</a>                                    <img src="${img.src}" alt="${img.alt || 'N/A'}"><br>
                                    <strong>Alt Text:</strong> ${img.alt || 'N/A'}
                                </div>
                            `);
                        });

                        $('.results').show();
                    },
                    error: function(xhr, status, error) {
                        $('.loading').hide();
                        $('.error').text('Error crawling URL: ' + error).show();
                    }
                });
            });
        });
    </script>
</body>
</html>
'''

async def crawl_url(url):
    crawler_cfg = CrawlerRunConfig(
        exclude_social_media_links=True,
        wait_for_images=True,
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=crawler_cfg)
        
        if result.success:
            return {
                'links': {
                    'internal': result.links.get('internal', []),
                    'external': result.links.get('external', [])
                },
                'media': {
                    'images': result.media.get('images', [])
                }
            }
        else:
            raise Exception(result.error_message)

@app.route('/')
def home():
    return HTML_TEMPLATE

@app.route('/crawl', methods=['POST'])
def handle_crawl():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        result = asyncio.run(crawl_url(url))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)