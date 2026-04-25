package com.lastmile.pedidos.model;

public enum EstadoPedido {
    PENDIENTE,       // Recién creado, sin conductor asignado
    ASIGNADO,        // El orquestador asignó un conductor
    EN_CAMINO,       // El conductor recogió el paquete
    ENTREGADO,       // Entrega exitosa
    FALLIDO,         // No se pudo entregar
    CANCELADO        // Cancelado por el cliente u operación
}
