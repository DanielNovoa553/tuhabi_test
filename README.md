# tuhabi_test
Para el Api use Flask Api
Para la conexion a la base de datos con gestor MySQL Contro Center
Para el requerimiento de me gusta lo mejor es hacer una nueva tabla para relacionar el id de la propiedad con el id del usuario.

CREATE TABLE likes (
    id_likes int NOT NULL,
    id_usuario int NOT NULL,
    id_property int NOT NULL,
    PRIMARY KEY (id_likes)
);

y para el total de me gusta lo mejor es agregar un campo a la tabla property  donde se llevara la cantida de likes, esto para evitar que se recorra la tabla likes cada vez que queramos el total de likes, solo se tendria que hacer un select a este campo.
