package com.lastmile.pedidos.service;

import com.lastmile.pedidos.config.PedidoMapper;
import com.lastmile.pedidos.dto.PedidoDTO;
import com.lastmile.pedidos.exception.PedidoNotFoundException;
import com.lastmile.pedidos.exception.TransicionEstadoInvalidaException;
import com.lastmile.pedidos.model.EstadoPedido;
import com.lastmile.pedidos.model.Pedido;
import com.lastmile.pedidos.repository.PedidoRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class PedidoService {

    private final PedidoRepository pedidoRepository;
    private final PedidoMapper mapper;

    // ── Crear pedido ───────────────────────────────────────────────────────────
    @Transactional
    public PedidoDTO.PedidoResponse crearPedido(PedidoDTO.CrearPedidoRequest request) {
        log.info("Creando pedido para cliente: {}", request.getClienteNombre());
        Pedido pedido = mapper.toEntity(request);
        Pedido guardado = pedidoRepository.save(pedido);
        log.info("Pedido creado con id: {}", guardado.getId());
        return mapper.toResponse(guardado);
    }

    // ── Obtener pedido por ID ──────────────────────────────────────────────────
    @Transactional(readOnly = true)
    public PedidoDTO.PedidoResponse obtenerPedido(Long id) {
        Pedido pedido = buscarOFallar(id);
        return mapper.toResponse(pedido);
    }

    // ── Listar todos (resumen) ─────────────────────────────────────────────────
    @Transactional(readOnly = true)
    public List<PedidoDTO.PedidoResumenResponse> listarPedidos() {
        return pedidoRepository.findAll().stream()
                .map(mapper::toResumen)
                .collect(Collectors.toList());
    }

    // ── Listar por estado ──────────────────────────────────────────────────────
    @Transactional(readOnly = true)
    public List<PedidoDTO.PedidoResumenResponse> listarPorEstado(EstadoPedido estado) {
        return pedidoRepository.findByEstado(estado).stream()
                .map(mapper::toResumen)
                .collect(Collectors.toList());
    }

    // ── Listar pendientes (para el orquestador) ────────────────────────────────
    @Transactional(readOnly = true)
    public List<PedidoDTO.PedidoResumenResponse> listarPendientes() {
        return pedidoRepository.findPendientesOrdenados().stream()
                .map(mapper::toResumen)
                .collect(Collectors.toList());
    }

    // ── Actualizar estado (llamado por el orquestador o el conductor) ──────────
    @Transactional
    public PedidoDTO.PedidoResponse actualizarEstado(Long id,
                                                      PedidoDTO.ActualizarEstadoRequest request) {
        Pedido pedido = buscarOFallar(id);
        validarTransicion(pedido.getEstado(), request.getEstado());

        pedido.setEstado(request.getEstado());

        if (request.getConductorId() != null) {
            pedido.setConductorId(request.getConductorId());
        }

        log.info("Pedido {} → estado actualizado a {}", id, request.getEstado());
        return mapper.toResponse(pedidoRepository.save(pedido));
    }

    // ── Cancelar pedido ────────────────────────────────────────────────────────
    @Transactional
    public void cancelarPedido(Long id) {
        Pedido pedido = buscarOFallar(id);
        Set<EstadoPedido> cancelables = Set.of(
                EstadoPedido.PENDIENTE, EstadoPedido.ASIGNADO
        );
        if (!cancelables.contains(pedido.getEstado())) {
            throw new TransicionEstadoInvalidaException(
                    "No se puede cancelar un pedido en estado " + pedido.getEstado()
            );
        }
        pedido.setEstado(EstadoPedido.CANCELADO);
        pedidoRepository.save(pedido);
        log.info("Pedido {} cancelado", id);
    }

    // ── Helper ─────────────────────────────────────────────────────────────────
    private Pedido buscarOFallar(Long id) {
        return pedidoRepository.findById(id)
                .orElseThrow(() -> new PedidoNotFoundException(
                        "Pedido con id " + id + " no encontrado"
                ));
    }

    /**
     * Máquina de estados del pedido.
     * Define qué transiciones son válidas.
     */
    private void validarTransicion(EstadoPedido actual, EstadoPedido nuevo) {
        boolean valida = switch (actual) {
            case PENDIENTE  -> nuevo == EstadoPedido.ASIGNADO  || nuevo == EstadoPedido.CANCELADO;
            case ASIGNADO   -> nuevo == EstadoPedido.EN_CAMINO || nuevo == EstadoPedido.CANCELADO;
            case EN_CAMINO  -> nuevo == EstadoPedido.ENTREGADO || nuevo == EstadoPedido.FALLIDO;
            default         -> false;  // ENTREGADO, FALLIDO, CANCELADO son estados finales
        };

        if (!valida) {
            throw new TransicionEstadoInvalidaException(
                    "Transición inválida: " + actual + " → " + nuevo
            );
        }
    }
}
