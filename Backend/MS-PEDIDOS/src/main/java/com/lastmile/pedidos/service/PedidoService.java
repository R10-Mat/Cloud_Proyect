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
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

@Service
@RequiredArgsConstructor
@Slf4j
public class PedidoService {

    private final PedidoRepository pedidoRepository;
    private final PedidoMapper mapper;

    @Transactional
    public PedidoDTO.PedidoResponse crearPedido(PedidoDTO.CrearPedidoRequest request) {
        log.info("Creando pedido para cliente: {}", request.getClienteNombre());
        Pedido pedido = mapper.toEntity(request);
        Pedido guardado = pedidoRepository.save(pedido);
        log.info("Pedido creado con id: {}", guardado.getId());
        return mapper.toResponse(guardado);
    }

    @Transactional(readOnly = true)
    public PedidoDTO.PedidoResponse obtenerPedido(Long id) {
        Pedido pedido = buscarOFallar(id);
        return mapper.toResponse(pedido);
    }

    @Transactional(readOnly = true)
    public List<PedidoDTO.PedidoResumenResponse> listarPedidos() {
        return pedidoRepository.findAll().stream()
                .map(mapper::toResumen)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<PedidoDTO.PedidoResumenResponse> listarPorEstado(EstadoPedido estado) {
        return pedidoRepository.findByEstado(estado).stream()
                .map(mapper::toResumen)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<PedidoDTO.PedidoResumenResponse> listarPendientes() {
        return pedidoRepository.findPendientesOrdenados().stream()
                .map(mapper::toResumen)
                .collect(Collectors.toList());
    }


    @Transactional(readOnly = true)
    public Map<String, Object> listarPedidosPaginado(Pageable pageable) {
        Page<Pedido> page = pedidoRepository.findAll(pageable);
        return buildPageResponse(page);
    }

    @Transactional(readOnly = true)
    public Map<String, Object> listarPorEstadoPaginado(EstadoPedido estado, Pageable pageable) {
        Page<Pedido> page = pedidoRepository.findByEstado(estado, pageable);
        return buildPageResponse(page);
    }

    @Transactional(readOnly = true)
    public Map<String, Object> listarPendientesPaginado(Pageable pageable) {
        Page<Pedido> page = pedidoRepository.findPendientesOrdenados(pageable);
        return buildPageResponse(page);
    }

    private Map<String, Object> buildPageResponse(Page<Pedido> page) {
        List<PedidoDTO.PedidoResumenResponse> content = page.getContent().stream()
                .map(mapper::toResumen)
                .collect(Collectors.toList());
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("content", content);
        response.put("totalElements", page.getTotalElements());
        response.put("totalPages", page.getTotalPages());
        response.put("page", page.getNumber());
        response.put("size", page.getSize());
        return response;
    }

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

    private Pedido buscarOFallar(Long id) {
        return pedidoRepository.findById(id)
                .orElseThrow(() -> new PedidoNotFoundException(
                        "Pedido con id " + id + " no encontrado"
                ));
    }

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
