# UserApp

A reusable Django app that provides a customizable user system for all Django projects. This app is designed to be general-purpose so it can be easily integrated into different projects.

---

## ✨ Features

- 🔑 Custom user model (ready to extend)
- 📧 SMS verification support
- ✅ Authentication & permissions
- ⚙️ Django REST Framework (DRF)
- 📂 Clean and reusable structure

---

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/parsaferdosi/UserApp.git
   ```

2. Add the `user` app to your Django `INSTALLED_APPS` in `setting.py` :
   ```python
   INSTALLED_APPS = [
       ...
       'user',
   ]
   ```
   And at the end of `setting.py` file include this line
   ```python
   AUTH_USER_MODEL = 'user.Account'
   ```
   

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

---

## 🚀 Usage

- Extend or use the built-in custom user model.
- Use authentication, verification, and permission features.
- Integrate easily with DRF for API development.

---

## 📖 Project Structure

```
UserApp/
├── user/          # Main Django app
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
