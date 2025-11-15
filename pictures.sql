USE Pictures;

-- Crea la tabla 'pictures' si no existe
CREATE TABLE IF NOT EXISTS pictures (
    id VARCHAR(36) PRIMARY KEY,
    path VARCHAR(255),
    date TIMESTAMP
);

-- Crea la tabla 'tags' si no existe
CREATE TABLE IF NOT EXISTS tags (
    tag VARCHAR(32) NOT NULL,
    pictures_id VARCHAR(36) NOT NULL,
    confidence VARCHAR(255),
    date TIMESTAMP,
    
    -- Clave primaria compuesta
    PRIMARY KEY (tag, pictures_id),
    
    -- Clave foránea que referencia a 'pictures(id)'
    FOREIGN KEY (pictures_id) REFERENCES pictures(id)
);