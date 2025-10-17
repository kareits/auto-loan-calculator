# КАЛЬКУЛЯТОР ДЛЯ АВТОКРЕДИТОВ
import os

import numpy_financial as npf
import streamlit as st
from PIL import Image


# Словари ставок
car_rate_dict = {"used_car": 0.33, "new_car": 0.28}
insurance_rates = {"new_car": 0.045, "used_car": 0.025}

# Путь к PNG-логотипу
logo_path = os.path.join(os.path.dirname(__file__), "media", "solva_logo.png")
logo_image = Image.open(logo_path)

# Заголовок с логотипом
col1, col2 = st.columns([1, 0.2])
with col1:
    st.markdown(
        '<span style="font-size:32px; font-weight:bold;">Калькулятор автокредитования</span>',
        unsafe_allow_html=True
    )
with col2:
    st.image(logo_image, width=120)  # ширина 120 px

# Выбор типа автомобиля
car_type = st.selectbox(
    "Тип автомобиля", ["Новый автомобиль", "Автомобиль с пробегом"]
)
car_key = "new_car" if car_type == "Новый автомобиль" else "used_car"

# Стоимость автомобиля
car_price = st.number_input(
    "Стоимость автомобиля (в тенге)",
    min_value=0,
    max_value=200_000_000,
    value=10_000_000,
    step=100_000
)

# Отображаем значение с разрядами
st.write(f"💰 Введенная стоимость автомобиля: **{car_price:,.0f} тенге**")

# Первоначальный взнос
if car_key == "new_car":
    default_down_payment = 20
else:
    default_down_payment = 30

down_payment_percent = st.slider(
    "Первоначальный взнос (%)", 0, 100, default_down_payment, step=5
)

# Расчет страховой премии
st.subheader("Страхование КАСКО")
insurance_switch = st.toggle("Страхование Каско на 1 год", value=False)
insurance_premium = 0
if insurance_switch:
    insurance_premium = car_price * insurance_rates[car_key]
    st.write(
        f"💰 Стоимость страховой премии: **{insurance_premium:,.0f} тенге**"
    )
else:
    st.write("КАСКО не выбрано.")

# Сумма займа со страховой премией
principal_net = car_price * (1 - down_payment_percent / 100)
loan_amount = principal_net + insurance_premium 

# Субсидия от дистрибьютера
has_subsidy = False
if car_key == "new_car":
    st.subheader("Субсидия от дистрибьютера")
    has_subsidy = st.toggle("Наличие субсидии от дистрибьютера", value=False)
subsidy_percent = 0
subsidy_amount = 0
if has_subsidy:
    subsidy_percent = st.slider("Размер субсидии (%)", 0, 20, 5, step=1)
    subsidy_amount = car_price * subsidy_percent / 100
    st.write(f"💸 Сумма субсидии: **{subsidy_amount:,.0f} тенге**")
else:
    st.write("Субсидия не применяется.")

# Срок займа
st.subheader("Срок займа")
loan_term = st.slider("Срок займа (в месяцах)", 0, 84, 60, step=12)

# Расчет аннуитетного платежа и общей суммы вознаграждения
rate = car_rate_dict[car_key]
monthly_rate = rate / 12
annuity_factor = (
    (monthly_rate * (1 + monthly_rate) ** loan_term)
    / ((1 + monthly_rate) ** loan_term - 1)
)
monthly_payment = loan_amount * annuity_factor
total_payment = monthly_payment * loan_term
total_interest = total_payment - loan_amount
if has_subsidy:
    total_interest -= subsidy_amount
    monthly_payment = (loan_amount + total_interest) / loan_term
    monthly_rate = npf.rate(loan_term, -monthly_payment, loan_amount, 0, when=0)
    rate = monthly_rate * 12

st.markdown(f"## Результаты расчета")
if has_subsidy and rate < 0:
    st.write(f"#### Невозможно рассчитать. Измените первоначальный взнос и/или размер субсидий!")
else:
    st.write(f"#### 📊 Сумма займа: **{loan_amount:,.0f} тенге**")
    st.write(f"#### 📈 Ставка вознаграждения: **{rate * 100:.1f}% годовых**")
    st.write(f"#### 💳 Ежемесячный платеж: {monthly_payment:,.0f} тенге")
    st.write(f"#### 🧾 Сумма переплаты: {total_interest:,.0f} тенге")
