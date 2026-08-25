"""Initial MainBD schema (app) aligned with KEDO DDL."""

from typing import Sequence, Union

from alembic import op

revision: str = "001_main_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE SCHEMA IF NOT EXISTS app")
    op.execute("SET search_path = app, public")

    op.execute(
        """
        CREATE TABLE departments (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE positions (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE consent_statuses (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE statuses (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE request_types (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            file_path TEXT
        );

        CREATE TABLE users (
            id BIGSERIAL PRIMARY KEY,
            phone TEXT,
            email TEXT UNIQUE,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            birth_date DATE,
            city TEXT,
            department_id BIGINT REFERENCES departments(id) ON DELETE SET NULL,
            hire_date DATE,
            position_id BIGINT REFERENCES positions(id) ON DELETE SET NULL,
            blocked_at DATE,
            block_reason TEXT
        );

        CREATE INDEX idx_users_department ON users(department_id);
        CREATE INDEX idx_users_position ON users(position_id);

        CREATE TABLE user_private_data (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            passport TEXT,
            inn TEXT,
            snils TEXT,
            bank_account TEXT,
            military_id TEXT,
            account_number TEXT,
            bik TEXT,
            bank_receiver TEXT,
            correspondent_account TEXT,
            kpp TEXT,
            contract_number TEXT,
            dismissal_date DATE,
            personal_data_deletion_date DATE
        );

        CREATE TABLE user_consent (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            document_path TEXT,
            purpose TEXT NOT NULL,
            signed_at TIMESTAMPTZ,
            valid_until DATE,
            consent_status_id BIGINT NOT NULL REFERENCES consent_statuses(id) ON DELETE SET NULL
        );

        CREATE INDEX idx_user_consent_user ON user_consent(user_id);

        CREATE TABLE requests (
            id BIGSERIAL PRIMARY KEY,
            employee_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            reviewer_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            approver_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            request_type_id BIGINT NOT NULL REFERENCES request_types(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            status_id BIGINT NOT NULL REFERENCES statuses(id) ON DELETE SET NULL,
            comment TEXT
        );

        CREATE INDEX idx_requests_employee ON requests(employee_id);
        CREATE INDEX idx_requests_status ON requests(status_id);

        CREATE TABLE document_files (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            request_id BIGINT NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
            file_path TEXT NOT NULL
        );

        CREATE TABLE notifications (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            request_id BIGINT REFERENCES requests(id) ON DELETE SET NULL,
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE INDEX idx_notifications_user_unread
            ON notifications(user_id, is_read, created_at DESC);

        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_requests_updated_at
        BEFORE UPDATE ON requests
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();

        CREATE OR REPLACE VIEW v_users AS
        SELECT
            u.id, u.phone, u.email, u.full_name, u.birth_date, u.city,
            d.name AS department, u.hire_date, p.name AS position,
            u.blocked_at, u.block_reason
        FROM users u
        LEFT JOIN departments d ON d.id = u.department_id
        LEFT JOIN positions p ON p.id = u.position_id;

        CREATE OR REPLACE VIEW v_requests AS
        SELECT
            r.id,
            r.employee_id,
            employee.full_name AS employee_name,
            r.reviewer_id,
            reviewer.full_name AS reviewer_name,
            r.approver_id,
            approver.full_name AS approver_name,
            rt.name AS request_type,
            s.name AS status,
            r.created_at,
            r.updated_at,
            r.comment
        FROM requests r
        JOIN users employee ON employee.id = r.employee_id
        LEFT JOIN users reviewer ON reviewer.id = r.reviewer_id
        LEFT JOIN users approver ON approver.id = r.approver_id
        LEFT JOIN request_types rt ON rt.id = r.request_type_id
        LEFT JOIN statuses s ON s.id = r.status_id;

        INSERT INTO departments (name) VALUES ('HR'), ('IT'), ('Finance')
        ON CONFLICT DO NOTHING;

        INSERT INTO positions (name) VALUES ('Работник'), ('HR'), ('Руководитель'), ('Администратор')
        ON CONFLICT DO NOTHING;

        INSERT INTO consent_statuses (name) VALUES ('Действует'), ('Истёк'), ('Отозван')
        ON CONFLICT DO NOTHING;

        INSERT INTO statuses (name) VALUES
        ('Создана'), ('На проверке'), ('На согласовании'),
        ('Одобрена'), ('Отклонена'), ('Закрыта')
        ON CONFLICT DO NOTHING;

        INSERT INTO request_types (name) VALUES
        ('Заявление'), ('Кадровый документ'), ('Прочее')
        ON CONFLICT DO NOTHING;
        """
    )


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS app CASCADE")
