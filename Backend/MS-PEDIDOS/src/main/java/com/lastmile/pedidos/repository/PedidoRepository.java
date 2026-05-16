package com.lastmile.pedidos.repository;

import com.lastmile.pedidos.model.EstadoPedido;
import com.lastmile.pedidos.model.Pedido;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

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

    // ── Overloads paginados ─────────────────────────────────────────────────
    Page<Pedido> findByEstado(EstadoPedido estado, Pageable pageable);

    @Query(
        value = "SELECT p FROM Pedido p WHERE p.estado = 'PENDIENTE' ORDER BY p.fechaCreacion ASC",
        countQuery = "SELECT COUNT(p) FROM Pedido p WHERE p.estado = 'PENDIENTE'"
    )
    Page<Pedido> findPendientesOrdenados(Pageable pageable);
}
