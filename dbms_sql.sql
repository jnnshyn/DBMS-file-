CREATE TABLE PRODUCT (
    PRODUCT_ID SERIAL PRIMARY KEY,
    PRODUCT_NAME VARCHAR(30) NOT NULL,
    PRODUCT_QOH INT NOT NULL,
    PRODUCT_PRICE DECIMAL(10, 2) NOT NULL,
    PRODUCT_DESC CHAR(255) NOT NULL,
    SUPP_ID  INT NOT NULL,
    FOREIGN KEY (SUPP_ID) REFERENCES SUPPLIER(SUPP_ID)
	ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ORDERS (
    ORDER_ID SERIAL PRIMARY KEY,
	ORDER_DATE DATE NOT NULL,
	ORDER_QUANTITY INT NOT NULL,
    ORDER_PAYMENT VARCHAR(30) NOT NULL,
    ORDER_TOTAL DECIMAL(10, 2) NOT NULL,
    PRODUCT_ID INT NOT NULL,
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID)
	ON DELETE CASCADE ON UPDATE CASCADE
);	

CREATE TABLE SUPPLIER (
    SUPP_ID SERIAL PRIMARY KEY,
    SUPP_NAME VARCHAR(50) NOT NULL,
    SUPP_EMAIL VARCHAR(50),
    SUPP_CONTACT VARCHAR(15) NOT NULL
);


CREATE TABLE SALES_REPORT (
    SALES_REPORT_ID SERIAL PRIMARY KEY,
    SALES_DATE DATE NOT NULL,
    SALES_TOTAL DECIMAL(10, 2) NOT NULL,
    PRODUCT_ID INT NOT NULL,
    ORDER_ID INT NOT NULL,
    SUPP_ID INT NOT NULL,
    FOREIGN KEY (SUPP_ID) REFERENCES SUPPLIER(SUPP_ID) ON DELETE CASCADE ON UPDATE CASCADE,	
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ORDER_ID) REFERENCES ORDERS(ORDER_ID) ON DELETE CASCADE ON UPDATE CASCADE
);



-- Trigger function definition
CREATE OR REPLACE FUNCTION add_sales_report() 
RETURNS TRIGGER AS $$
BEGIN
    -- Insert a new sales report record
    INSERT INTO SALES_REPORT (SALES_DATE, SALES_TOTAL, PRODUCT_ID, ORDER_ID, SUPP_ID)
    VALUES (
        NEW.ORDER_DATE,
        NEW.ORDER_TOTAL,
        NEW.PRODUCT_ID,
        NEW.ORDER_ID,
        (SELECT SUPP_ID FROM PRODUCT WHERE PRODUCT_ID = NEW.PRODUCT_ID)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger definition
CREATE TRIGGER after_order_insert
AFTER INSERT ON ORDERS
FOR EACH ROW
EXECUTE FUNCTION add_sales_report();
