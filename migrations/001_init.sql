CREATE TABLE IF NOT EXISTS app_users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(64) UNIQUE NOT NULL,
  password VARCHAR(128) NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  role VARCHAR(128) NOT NULL,
  status VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
  employee_id VARCHAR(32) PRIMARY KEY,
  full_name VARCHAR(255) NOT NULL,
  position VARCHAR(255) NOT NULL,
  department VARCHAR(255) NOT NULL,
  risk VARCHAR(64) NOT NULL,
  age INT NOT NULL,
  experience VARCHAR(64) NOT NULL,
  salary VARCHAR(64) NOT NULL,
  engagement VARCHAR(32) NOT NULL,
  performance VARCHAR(32) NOT NULL,
  work_hours VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS employee_factors (
  id SERIAL PRIMARY KEY,
  employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
  factor_name VARCHAR(255) NOT NULL,
  factor_value NUMERIC(5, 3) NOT NULL
);

INSERT INTO app_users (username, password, full_name, email, role, status)
VALUES
  ('admin', 'admin123', 'Администратор Системы', 'admin@x5ingroup.ru', 'Администратор', 'Активен'),
  ('manager', 'manager123', 'Менеджер Продаж', 'manager@x5ingroup.ru', 'Менеджер', 'Активен')
ON CONFLICT (username) DO NOTHING;

INSERT INTO employees (employee_id, full_name, position, department, risk, age, experience, salary, engagement, performance, work_hours)
VALUES
  ('EMP006', 'Albert Flores', 'Senior Accountant', 'Finance', 'Низкий', 40, '7 лет 0 мес', '$95,000', '88%', '92%', '38 hrs'),
  ('EMP014', 'Annette Black', 'QA Engineer', 'IT', 'Не прогнозируется', 34, '5 лет 4 мес', '$82,000', '84%', '89%', '40 hrs'),
  ('EMP012', 'Bessie Cooper', 'Team Lead', 'Customer Service', 'Не прогнозируется', 37, '8 лет 2 мес', '$90,000', '87%', '91%', '39 hrs'),
  ('EMP010', 'Cameron Williamson', 'DevOps Engineer', 'IT', 'Низкий', 31, '6 лет 1 мес', '$105,000', '90%', '94%', '41 hrs')
ON CONFLICT (employee_id) DO NOTHING;

INSERT INTO employee_factors (employee_id, factor_name, factor_value)
VALUES
  ('EMP006', 'Satisfaction Score', 0.120),
  ('EMP006', 'Work Hours Per Week', 0.080),
  ('EMP006', 'Last Evaluation', 0.060),
  ('EMP006', 'Salary', 0.040)
ON CONFLICT DO NOTHING;
