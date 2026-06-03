# UserApp

A reusable Django app that provides a customizable user system for all Django projects. This app is designed to be general-purpose so it can be easily integrated into different projects.

---

## ✨ Features

- 🔑 Custom user model with Email and Username login support (`AUTH_USER_MODEL`)
- 🔒 2FA Authentication (OTP generation & SMS integration)
- 🚀 JWT Session Management (`rest_framework_simplejwt`)
- ⚡  Redis caching for OTP state and Attempt Tracking and Manage User session
- 📂 Clean architecture ("Fat Serializers, Skinny Views")
- 🛠️ Easily swappable SMS providers (Built-in Console and SMS.ir support)

---

## 📦 Installation

1. Clone the repository into your Django project:
   ```bash
   git clone https://github.com/parsaferdosi/UserApp.git
   ```

2. Add the `user` and `rest_framework_simplejwt` apps to your Django `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'rest_framework_simplejwt',
       'user',
   ]
   ```

3. Configure your custom user model in `settings.py`:
   ```python
   AUTH_USER_MODEL = 'user.Account'
   ```

4. Configure Redis, SMS, and 2FA Settings in your `settings.py`:
   ```python
   # -------------------------
   # UserApp Settings
   # -------------------------
   
   # Redis Connection Settings
   REDIS_HOST = "localhost"
   REDIS_PORT = 6379
   REDIS_PASSWORD = None
   REDIS_DATABASES = {"otp": 0, "cache": 1, "session": 2, "queue": 3}

   # SMS Provider Settings
   SMS_PROVIDER = "console" # Options: "console" or "sms_ir"
   # SMS_API_KEY = "your_sms_ir_api_key"
   # SMS_LINE_NUMBER = "your_sms_ir_line_number"

   # 2FA Settings
   TTL_2FA = 120 # Seconds until OTP expires
   MAX_2FA_ATTEMPTS = 3
   ```

5. Run migrations:
   ```bash
   python manage.py makemigration
   python manage.py migrate
   ```

---

## 🚀 API Endpoints

Once included in your main `urls.py`, the following REST API endpoints will be available:
- `POST /register/` — Register a new account
- `POST /login/` — Request OTP via SMS
- `POST /login/authorization/` — Verify OTP and receive JWT tokens
- `POST /logout/` — Invalidate the current session
- `GET /profile/` — Retrieve user profile
- `PUT /profile/` — Update user profile
- `PUT /profile/change_password/` — Change user password
- `DELETE /profile/delete_account/` — Delete user account
- `POST /token/refresh/` — Refresh the JWT access token

---

## 📖 Project Structure

```text
UserApp/
├── user/          # Main Django app (Models, API Views, DRF Serializers)
├── utils/         # Helper modules (Redis Singleton Manager, SMS Providers, Generators)
├── LICENSE
├── README.md
└── .gitignore
```

---

## 📝 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Parsa Ferdosi Zade**  
- GitHub: [@parsaferdosi](https://github.com/parsaferdosi)
