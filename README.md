# Datamed Server - Wersja zdockeryzowana

**Author:** Jan Szymański  
**Project:** Protokoły sieci web, technologie chmurowe, bezpieczeństwo aplikacji webowych
### Żeby uruchomić projekt (od zera)
1. uruchom skrypt start.sh
2. powinny wtedy uruchomić się 2 endpointy do połączenia:
- https://localhost/ do frontendu
- https://localhost/auth do keycloaka, może być konieczna edycja valid redirect URI i web origins na https://localhost/, oraz ustawienie możliści rejestracji przez użytkowników
3. W razie konieczności pełnego resetu, uruchomić skrypt cleanup.sh
### Projekt składa się z 6 kontenerów:
1. Frontend (alpine)
2. Reverse proxy (nginx)
3. Backend (python 11-slim)
4. Pamięć do PDF'ów (minio)
5. Baza danych (Postgres)
6. Middleware (Keycloak)
