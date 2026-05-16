package com.lastmile.pedidos.controller;

import com.lastmile.pedidos.dto.PedidoDTO;
import com.lastmile.pedidos.model.EstadoPedido;
import com.lastmile.pedidos.service.PedidoService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;

@RestController
@RequestMapping("/api/pedidos")
@RequiredArgsConstructor
public class PedidoController {

    private final PedidoService pedidoService;

    // ── POST /api/pedidos ──────────────────────────────────────────────────────
    // Crear un nuevo pedido con sus paquetes
    @PostMapping
    public ResponseEntity<PedidoDTO.PedidoResponse> crearPedido(
            @Valid @RequestBody PedidoDTO.CrearPedidoRequest request) {

        PedidoDTO.PedidoResponse response = pedidoService.crearPedido(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // ── GET /api/pedidos ───────────────────────────────────────────────────────────
    // Listar pedidos paginados, opcionalmente filtrar por estado
    @GetMapping
    public ResponseEntity<Map<String, Object>> listarPedidos(
            @RequestParam(required = false) EstadoPedido estado,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {

        size = Math.max(1, Math.min(100, size));
        page = Math.max(0, page);
        PageRequest pageable = PageRequest.of(page, size, Sort.by("id").descending());

        if (estado != null) {
            return ResponseEntity.ok(pedidoService.listarPorEstadoPaginado(estado, pageable));
        }
        return ResponseEntity.ok(pedidoService.listarPedidosPaginado(pageable));
    }

    // ── GET /api/pedidos/pendientes ────────────────────────────────────────────
    // Endpoint dedicado para el MS-Orquestador: obtiene pedidos sin asignar (paginado)
    @GetMapping("/pendientes")
    public ResponseEntity<Map<String, Object>> listarPendientes(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {

        size = Math.max(1, Math.min(100, size));
        page = Math.max(0, page);
        PageRequest pageable = PageRequest.of(page, size);
        return ResponseEntity.ok(pedidoService.listarPendientesPaginado(pageable));
    }

    // ── GET /api/pedidos/{id} ──────────────────────────────────────────────────
    // Detalle completo con todos sus paquetes
    @GetMapping("/{id}")
    public ResponseEntity<PedidoDTO.PedidoResponse> obtenerPedido(@PathVariable Long id) {
        return ResponseEntity.ok(pedidoService.obtenerPedido(id));
    }

    // ── PATCH /api/pedidos/{id}/estado ─────────────────────────────────────────
    // Actualiza el estado del pedido (lo usará el MS-Orquestador y el conductor)
    @PatchMapping("/{id}/estado")
    public ResponseEntity<PedidoDTO.PedidoResponse> actualizarEstado(
            @PathVariable Long id,
            @Valid @RequestBody PedidoDTO.ActualizarEstadoRequest request) {

        return ResponseEntity.ok(pedidoService.actualizarEstado(id, request));
    }

    // ── DELETE /api/pedidos/{id} ───────────────────────────────────────────────
    // Cancela el pedido (solo si está en estado PENDIENTE o ASIGNADO)
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> cancelarPedido(@PathVariable Long id) {
        pedidoService.cancelarPedido(id);
        return ResponseEntity.noContent().build();
    }

    // ── GET /api/pedidos/health ────────────────────────────────────────────────
    @GetMapping("/health")
    public ResponseEntity<Object> health() {
        return ResponseEntity.ok(java.util.Map.of("status", "ok", "service", "ms-pedidos"));
    }
}
