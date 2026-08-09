import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8088

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def main():
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    
    Handler = CustomHTTPRequestHandler
    Handler.extensions_map.update({
        '.html': 'text/html; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.png': 'image/png',
    })

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print("==========================================================")
        print(f" Servidor Local de Testes do Publicoverso Ativo")
        print(f" Endereco: {url}")
        print(" Pressione Ctrl + C no terminal para encerrar.")
        print("==========================================================")
        
        try:
            webbrowser.open(url)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor local encerrado com sucesso.")
            sys.exit(0)

if __name__ == '__main__':
    main()
