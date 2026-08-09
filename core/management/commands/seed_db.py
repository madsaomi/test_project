import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress
from profiles.models import StudentProfile, EmployerProfile
from vacancies.models import Vacancy, Category
from applications.models import Application

User = get_user_model()


class Command(BaseCommand):
    help = "Заполняет базу данных демо-данными"

    def handle(self, *args, **options):
        self.stdout.write("Создание категорий...")
        categories_data = [
            "Python", "Frontend", "Backend", "Design", "Marketing",
            "SMM", "QA", "Data Science", "Mobile", "DevOps",
        ]
        for name in categories_data:
            Category.objects.get_or_create(name=name, slug=name.lower().replace(" ", "-"))

        self.stdout.write("Создание работодателей...")
        employers_data = [
            {"company_name": "UzDev", "company_description": "Крупная IT-компания в Ташкенте"},
            {"company_name": "DigitalLab", "company_description": "Маркетинговое агентство"},
            {"company_name": "StartupValley", "company_description": "Стартап-инкубатор"},
            {"company_name": "DataVision", "company_description": "Аналитическая платформа"},
            {"company_name": "WebCraft", "company_description": "Веб-студия"},
        ]
        employers = []
        for i, data in enumerate(employers_data, 1):
            user, _ = User.objects.get_or_create(
                email=f"employer{i}@example.com",
                defaults={
                    "role": "employer",
                    "first_name": f"Company {i}",
                },
            )
            user.set_password("password123")
            user.save()
            profile, _ = EmployerProfile.objects.get_or_create(
                user=user, defaults=data
            )
            employers.append(profile)

        self.stdout.write("Создание студентов...")
        first_names = ["Азиза", "Тимур", "Малика", "Жахонгир", "Нигина", "Шахзод", "Дилноза", "Сардор", "Зарина", "Бекзод"]
        last_names = ["Каримова", "Рахимов", "Азизова", "Юлдашев", "Арифова", "Акбаров", "Усманова", "Турсунов", "Мирзаева", "Нормуродов"]
        students = []
        for i in range(10):
            user, _ = User.objects.get_or_create(
                email=f"student{i+1}@example.com",
                defaults={
                    "role": "student",
                    "first_name": first_names[i],
                    "last_name": last_names[i],
                },
            )
            user.set_password("password123")
            user.save()
            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "city": random.choice(["Ташкент", "Самарканд", "Бухара", "Наманган", "Фергана"]),
                    "education": "ТУИТ" if i % 2 == 0 else "Национальный университет Узбекистана",
                    "experience": f"{random.randint(0, 2)} года опыта",
                },
            )
            students.append(profile)

        self.stdout.write("Создание вакансий...")
        categories = list(Category.objects.all())
        titles = [
            "Стажёр Python-разработчик", "Junior Frontend-разработчик",
            "Стажёр UI/UX дизайнер", "Младший SMM-менеджер",
            "Стажёр аналитик данных", "Junior QA-инженер",
            "Стажёр backend-разработчик", "Младший DevOps-инженер",
            "Стажёр мобильный разработчик", "Junior продуктовый дизайнер",
            "Стажёр data scientist", "Младший маркетолог",
            "Стажёр web-разработчик", "Junior системный аналитик",
            "Стажёр iOS-разработчик", "Младший PR-менеджер",
            "Стажёр Android-разработчик", "Junior бизнес-аналитик",
            "Стажёр тестировщик", "Младший project manager",
            "Стажёр SEO-специалист", "Junior Golang-разработчик",
            "Стажёр технический писатель", "Младший product manager",
            "Стажёр информационная безопасность", "Junior React-разработчик",
            "Стажёр 1С", "Младший HR-менеджер",
            "Стажёр GameDev", "Junior Kotlin-разработчик",
        ]
        vacancies = []
        for i, title in enumerate(titles):
            employer = random.choice(employers)
            category = random.choice(categories)
            vacancy, _ = Vacancy.objects.get_or_create(
                title=title,
                employer=employer,
                defaults={
                    "description": f"Мы ищем талантливого стажёра на позицию {title.lower()}. Отличная возможность начать карьеру!",
                    "requirements": "Базовые знания в области, желание учиться, ответственность",
                    "conditions": "оформление по ТК РУз, гибкий график, бесплатные обеды",
                    "salary": f"{random.choice(['', '3 000 000 - 5 000 000 сум', '5 000 000 - 8 000 000 сум', '8 000 000 - 12 000 000 сум', 'Оплачиваемая', 'Неоплачиваемая'])}",
                    "city": random.choice(["Ташкент", "Самарканд", "Бухара", "Наманган", "Фергана", "Удалённо"]),
                    "work_type": random.choice(["remote", "office", "hybrid"]),
                    "category": category,
                    "is_active": True,
                },
            )
            vacancies.append(vacancy)

        self.stdout.write("Создание откликов...")
        for _ in range(20):
            vacancy = random.choice(vacancies)
            student = random.choice(students)
            try:
                Application.objects.create(
                    vacancy=vacancy,
                    student=student,
                    status=random.choice(["sent", "viewed", "invited", "rejected"]),
                    cover_letter="Я очень заинтересован в этой позиции и хочу развиваться в данной сфере.",
                )
            except Exception:
                pass

        self.stdout.write("Создание админа...")
        try:
            User.objects.create_superuser(
                email="admin@admin.com",
                password="admin123",
                role="employer",
            )
            self.stdout.write(self.style.SUCCESS(
                "  Админ создан: admin@admin.com / admin123"
            ))
        except Exception:
            pass

        self.stdout.write("Подтверждение email для тестовых аккаунтов...")
        PASSWORD = "password123"
        for user in User.objects.all():
            EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"verified": True, "primary": True},
            )

        self.stdout.write("Настройка сайта...")
        site = Site.objects.get_current()
        site.domain = "localhost:8000"
        site.name = "StudCareer"
        site.save()

        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write(self.style.SUCCESS("━━━━━━━ ТЕСТОВЫЕ АККАУНТЫ ━━━━━━━"))
        self.stdout.write(self.style.SUCCESS(f"  Пароль для всех: {PASSWORD}"))
        self.stdout.write("")
        self.stdout.write("  👤 Студенты:")
        for i in range(1, 11):
            self.stdout.write(f"     student{i}@example.com")
        self.stdout.write("")
        self.stdout.write("  💼 Работодатели:")
        for i in range(1, 6):
            self.stdout.write(f"     employer{i}@example.com")
        self.stdout.write("")
        self.stdout.write("  🔑 Админ:")
        self.stdout.write("     admin@admin.com / admin123")
        self.stdout.write(self.style.SUCCESS("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("База данных успешно заполнена!"))
