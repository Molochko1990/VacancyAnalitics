const text = "Добро пожаловать на сайт, на нем вы найдете подробную информацию о разработчике игр. Приятного чтения!";

const textElement = document.querySelector("#animatedText");
let index = 0;
let isDeleting = false;

function typeEffect() {
    if (!isDeleting) {
        // Эффект набора текста
        if (index < text.length) {
            textElement.textContent += text[index];
            index++;
            setTimeout(typeEffect, 40); // Скорость набора
        } else {
            // Пауза перед удалением
            isDeleting = true;
            setTimeout(typeEffect, 1000); // Пауза после завершения набора
        }
    } else {
        // Плавное исчезновение текста
        let opacity = 1;
        const fadeOut = () => {
            if (opacity > 0) {
                opacity -= 0.05;
                textElement.style.opacity = opacity;
                setTimeout(fadeOut, 30); // Скорость исчезновения
            } else {
                // Сбрасываем текст и начинаем новый набор
                textElement.textContent = '';
                textElement.style.opacity = 1; // Восстановление начальной прозрачности
                setTimeout(typeEffect, 500); // Пауза перед началом нового набора
            }
        };
        fadeOut();
    }
}

typeEffect();
