# КАЛЬКУЛЯТОР ДЛЯ АВТОКРЕДИТОВ

import streamlit as st


# Словари ставок
car_rate_dict = {"used_car": 0.33, "new_car": 0.28}
insurance_rates = {"new_car": 0.045, "used_car": 0.025}

# Заголовок приложения
st.title("Калькулятор автокредитования")


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
loan_amount_display = principal_net + insurance_premium 

# Субсидия от дистрибьютера
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

# Агентское вознаграждение
st.subheader("Агентское вознаграждение дилерскому центру (с НДС)")
agent_fee_percent = st.slider(
    "Размер агентского вознаграждения (%)", 0.0, 10.0, 0.0, step=0.1
)
agent_fee_amount = principal_net * agent_fee_percent / 100
st.write(
    f"💸 Сумма агентского вознаграждения ДЦ: **{agent_fee_amount:,.0f} тенге**"
)

# Расчет суммы займа (с учетом субсидий и агентской комиссии)
loan_amount = (
    principal_net + insurance_premium - subsidy_amount + agent_fee_amount
)

# Срок займа
st.subheader("Срок займа")
loan_term = st.slider("Срок займа (в месяцах)", 0, 84, 60, step=12)

# Расчет аннуитетного платежа
rate = car_rate_dict[car_key]
monthly_rate = rate / 12
annuity_factor = (
    (monthly_rate * (1 + monthly_rate) ** loan_term)
    / ((1 + monthly_rate) ** loan_term - 1)
)
monthly_payment = loan_amount * annuity_factor

# Пересчет эффективной годовой ставки (APR)
# Решаем обратную задачу: какая ставка даёт такой же платёж
# при исходном долге без субсидии
def find_effective_rate(principal, payment, term):
    # численный подбор ставки методом Ньютона
    r = 0.25 / 12  # начальное приближение
    for _ in range(100):
        annuity_factor = (r * (1 + r) ** term) / ((1 + r) ** term - 1)
        f = principal * annuity_factor - payment
        df = (
            (
                principal * ((1 + r) ** term * ((1 + r) ** term - 1)
                             - (r * term * (1 + r) ** (term - 1)))
            )
            / ((1 + r) ** term - 1) ** 2
        )
        try:
            r -= f / df
        except ZeroDivisionError:
            st.warning("⚠ Деление на ноль при расчете. Расчет остановлен.")
            break
        if abs(f) < 1e-6:
            break
        return r * 12  # годовая ставка
if has_subsidy or agent_fee_percent:
    effective_rate = find_effective_rate(
        loan_amount_display, monthly_payment, loan_term
    )

total_payment = monthly_payment * loan_term
overpayment = total_payment - loan_amount

st.markdown(f"## Результаты расчета")
if has_subsidy and effective_rate < 0:
    st.write(f"#### Невозможно рассчитать. Измените первоначальный взнос и/или размер субсидий!")
else:
    st.write(f"#### 📊 Сумма займа: **{loan_amount_display:,.0f} тенге**")
    if has_subsidy or agent_fee_percent:
        st.write(f"#### 📈 Ставка вознаграждения: **{effective_rate * 100:.1f}% годовых**")
    else:
        st.write(f"#### 📈 Ставка вознаграждения: **{rate * 100:.1f}% годовых**")
    st.write(f"#### 💳 Ежемесячный платеж: {monthly_payment:,.0f} тенге")
    st.write(f"#### 🧾 Сумма переплаты: {overpayment:,.0f} тенге")
