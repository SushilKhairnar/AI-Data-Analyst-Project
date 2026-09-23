USE AI_Data_Analyst;
select * from departments

UPDATE departments
SET department_id =
    CASE department_id
        WHEN '1.00' THEN 'D01'
        WHEN '2.00' THEN 'D02'
        WHEN '3.00' THEN 'D03'
        WHEN '4.00' THEN 'D04'
        WHEN '5.00' THEN 'D05'
    END;

ALTER TABLE departments
ALTER COLUMN department_id NVARCHAR(10) NOT NULL;

SELECT * 
FROM departments;

select * from employees

ALTER TABLE employees
ALTER COLUMN department_id NVARCHAR(10) NOT NULL;

sp_help employees;

UPDATE employees
SET employee_id =
    'E' + RIGHT(
        '000' + CAST(CAST(CAST(employee_id AS DECIMAL(10,2)) AS INT) AS VARCHAR(3)),
        3
    );

UPDATE employees
SET department_id =
    CASE department_id
        WHEN '1.00' THEN 'D01'
        WHEN '2.00' THEN 'D02'
        WHEN '3.00' THEN 'D03'
        WHEN '4.00' THEN 'D04'
        WHEN '5.00' THEN 'D05'
    END;

SELECT COUNT(*) AS employee_count
FROM employees;

SELECT department_id, COUNT(*) AS employee_count
FROM employees
GROUP BY department_id
ORDER BY department_id;

ALTER TABLE employees
ADD CONSTRAINT FK_Employees_Departments
FOREIGN KEY (department_id)
REFERENCES departments(department_id);

sp_help departments;

ALTER TABLE departments
ADD CONSTRAINT PK_Departments
PRIMARY KEY (department_id);

ALTER TABLE employees
ADD CONSTRAINT FK_Employees_Departments
FOREIGN KEY (department_id)
REFERENCES departments(department_id);

SELECT
    e.employee_id,
    e.employee_name,
    e.department_id,
    d.department_name
FROM employees e
JOIN departments d
    ON e.department_id = d.department_id
ORDER BY e.employee_id;

select * from customer

sp_help customer;

SELECT COUNT(*) AS total_customers
FROM customer;

SELECT *
FROM customer
ORDER BY customer_id;

SELECT
    segment,
    COUNT(*) AS customer_count
FROM customer
GROUP BY segment;

select * from orders

sp_help orders;

SELECT COUNT(*) AS total_orders
FROM orders;

SELECT
    status,
    COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY status;

ALTER TABLE orders
ADD CONSTRAINT FK_orders_customer
FOREIGN KEY (customer_id)
REFERENCES customer(customer_id);

SELECT
    o.order_id,
    o.customer_id,
    c.name AS customer_name,
    o.order_date,
    o.status
FROM orders o
JOIN customer c
    ON o.customer_id = c.customer_id
ORDER BY o.order_id;

SELECT
    fk.name AS foreign_key_name,
    OBJECT_NAME(fk.parent_object_id) AS child_table,
    OBJECT_NAME(fk.referenced_object_id) AS parent_table
FROM sys.foreign_keys fk
WHERE fk.parent_object_id = OBJECT_ID('orders');

select * from products

sp_help products;

SELECT COUNT(*) AS product_count
FROM products;

SELECT
    category,
    COUNT(*) AS product_count
FROM products
GROUP BY category
ORDER BY category;

SELECT TOP 10 *
FROM products
ORDER BY product_id;

select * from order_items

sp_help order_items

SELECT COUNT(*) AS order_item_count
FROM order_items;

SELECT TOP 10 *
FROM order_items
ORDER BY order_item_id;

ALTER TABLE order_items
ADD CONSTRAINT FK_order_items_orders
FOREIGN KEY (order_id)
REFERENCES orders(order_id);

ALTER TABLE order_items
ADD CONSTRAINT FK_order_items_products
FOREIGN KEY (product_id)
REFERENCES products(product_id);


SELECT
    oi.order_item_id,
    oi.order_id,
    oi.product_id,
    oi.quantity,
    p.product_name,
    p.category,
    p.price,
    p.cost
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
ORDER BY oi.order_item_id;

SELECT
    o.order_id,
    o.order_date,
    o.status,
    c.customer_id,
    c.name AS customer_name,
    oi.product_id,
    p.product_name,
    p.category,
    oi.quantity,
    p.price,
    p.cost
FROM orders o
JOIN customer c
    ON o.customer_id = c.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
ORDER BY o.order_id;

SELECT
    e.employee_id,
    e.employee_name,
    e.department_id,
    d.department_name,
    d.manager_name,
    e.job_role,
    e.city,
    e.salary
FROM employees e
JOIN departments d
    ON e.department_id = d.department_id
ORDER BY e.employee_id;

select * from orders

--How many orders does the company have?--

select count(order_id) as total_orders from orders

-- How many completed orders are there? --

select count(order_id) as completed_order 
from orders
where status = 'Delivered'

-- What is the total revenue?

select * from products
select * from order_items

select sum(oi.quantity * p.price) as total_revenue 
from order_items oi inner join products p
on p.product_id = oi.product_id

-- What is the total profit?

select sum(oi.quantity * p.price) - sum(p.cost * oi.quantity) as total_profit
from order_items oi inner join products p
on p.product_id = oi.product_id

-- How much revenue did each product category generate?

select p.category, sum(p.price * oi.quantity) as revenue_per_category
from products p inner join order_items oi
on oi.product_id = p.product_id
group by p.category
order by sum(p.price * oi.quantity) desc

-- Which products sold the highest number of units?

select top 10 p.product_id, p.product_name, sum(oi.quantity) as total_quantity
from products p inner join order_items oi
on p.product_id = oi.product_id
group by p.product_id, p.product_name
order by sum(oi.quantity) desc

-- What is the total sales revenue for each customer segment?

select * from customer
select * from orders
select * from order_items
select * from products

select c.segment, sum(p.price * oi.quantity) as total_revenue_by_c_segment
from customer c inner join orders o
on c.customer_id = o.customer_id
inner join order_items oi
on oi.order_id = o.order_id
inner join products p
on p.product_id = oi.product_id
group by c.segment
order by total_revenue_by_c_segment desc

-- What is the total sales revenue for each month?

select year(o.order_date) as years, 
       month(o.order_date) as months, 
       sum(oi.quantity * p.price) as revenue_by_month
from orders o inner join order_items oi
on o.order_id = oi.order_id
inner join products p 
on p.product_id = oi.product_id
group by year(o.order_date), month(o.order_date)

-- How many employees are in each department?

select d.department_name, count(e.employee_id) as emp_per_dept
from departments d inner join employees e
on d.department_id = e.department_id
group by d.department_name

-- What is the average salary in each department?

select d.department_name, avg(e.salary) as emp_per_dept
from departments d inner join employees e
on d.department_id = e.department_id
group by d.department_name

-- Cancellation / Refund Rate

select 
      COUNT(*) AS total_orders,

      count(case when status = 'Cancelled' then 1 end) 
      as cancellation,

      count(case when status = 'Refunded' then 1 end)
      as Refunding,

      count(case when status = 'Cancelled' then 1 end) * 100.0 
      / count(order_id) as cancellation,

      count(case when status = 'Refunded' then 1 end) * 100.0 
      / count(order_id) as Refunding
from orders


--What is the total revenue generated by Premium customers in 2025?

select sum(p.price * oi.quantity) as revenue_of_premium_cust
from customer c inner join orders o 
on c.customer_id = o.customer_id
inner join order_items oi 
on oi.order_id = o.order_id
inner join products p 
on p.product_id = oi.product_id
where c.segment = 'Premium' and year(o.order_date) = 2025

-- Which product category generated the highest revenue in 2025?

select top 1 p.category, sum(p.price * oi.quantity) as revenue_per_category
from products p inner join order_items oi 
on p.product_id = oi.product_id
inner join orders o 
on o.order_id = oi.order_id
where year(o.order_date) = 2025
group by p.category
order by revenue_per_category desc

-- Show the top 5 products by revenue for Premium customers -- 

select top 5 p.product_id, p.product_name, sum(p.price * oi.quantity) as revenue_per_category
from products p inner join order_items oi 
on p.product_id = oi.product_id
inner join orders o 
on o.order_id = oi.order_id
inner join customer c 
on c.customer_id = o.customer_id
where c.segment = 'Premium'
group by p.product_id, p.product_name
order by revenue_per_category desc