-- Deliberately minimal synthetic schema, NOT a dump or full OpenMRS schema.
-- All role references keep their foreign keys enabled during migration.
CREATE TABLE users (user_id INT PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE privilege (privilege VARCHAR(255) PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE role (
    role VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255),
    uuid CHAR(38) NOT NULL UNIQUE
) ENGINE=InnoDB;
CREATE TABLE user_role (
    user_id INT NOT NULL,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, role),
    CONSTRAINT fixture_user_role_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fixture_user_role_role FOREIGN KEY (role) REFERENCES role(role)
) ENGINE=InnoDB;
CREATE TABLE role_privilege (
    role VARCHAR(50) NOT NULL,
    privilege VARCHAR(255) NOT NULL,
    PRIMARY KEY (role, privilege),
    CONSTRAINT fixture_role_privilege_role FOREIGN KEY (role) REFERENCES role(role),
    CONSTRAINT fixture_role_privilege_privilege FOREIGN KEY (privilege) REFERENCES privilege(privilege)
) ENGINE=InnoDB;
CREATE TABLE role_role (
    parent_role VARCHAR(50) NOT NULL,
    child_role VARCHAR(50) NOT NULL,
    PRIMARY KEY (parent_role, child_role),
    CONSTRAINT fixture_role_role_parent FOREIGN KEY (parent_role) REFERENCES role(role),
    CONSTRAINT fixture_role_role_child FOREIGN KEY (child_role) REFERENCES role(role)
) ENGINE=InnoDB;
CREATE TABLE concept_name (
    concept_name_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL DEFAULT ''
) ENGINE=InnoDB;
CREATE TABLE encounter_type (
    encounter_type_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    creator INT NOT NULL,
    date_created DATETIME NOT NULL,
    retired TINYINT NOT NULL,
    uuid VARCHAR(38) NOT NULL UNIQUE,
    CONSTRAINT fixture_encounter_creator FOREIGN KEY (creator) REFERENCES users(user_id)
) ENGINE=InnoDB;
CREATE TABLE form (
    form_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    published TINYINT NOT NULL,
    encounter_type INT,
    creator INT NOT NULL,
    date_created DATETIME NOT NULL,
    retired TINYINT NOT NULL,
    uuid VARCHAR(38) NOT NULL UNIQUE,
    changed_by INT,
    date_changed DATETIME,
    retired_by INT,
    date_retired DATETIME,
    retired_reason TEXT,
    CONSTRAINT fixture_form_encounter FOREIGN KEY (encounter_type) REFERENCES encounter_type(encounter_type_id),
    CONSTRAINT fixture_form_creator FOREIGN KEY (creator) REFERENCES users(user_id)
) ENGINE=InnoDB;
INSERT INTO users VALUES (1), (2), (3);
