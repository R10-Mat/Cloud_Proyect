package com.lastmile.pedidos.repository;

import com.lastmile.pedidos.model.EstadoPedido;
import com.lastmile.pedidos.model.Pedido;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PedidoRepository extends JpaRepository<Pedido, Long> {

    // Filtrar por estado
    List<Pedido> findByEstado(EstadoPedido estado);

    // Buscar pedidos de un conductor (útil para el orquestador)
    List<Pedido> findByConductorId(Long conductorId);

    // Contar pedidos por estado (para analítica)
    long countByEstado(EstadoPedido estado);

    // Búsqueda por nombre de cliente (case-insensitive)
    List<Pedido> findByClienteNombreContainingIgnoreCase(String nombre);

    // Pedidos pendientes (sin conductor asignado)
    @Query("SELECT p FROM Pedido p WHERE p.estado = 'PENDIENTE' ORDER BY p.fechaCreacion ASC")
    List<Pedido> findPendientesOrdenados();
}
