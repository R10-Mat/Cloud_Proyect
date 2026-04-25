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

    // ── GET /api/pedidos ───────────────────────────────────────────────────────
    // Listar todos los pedidos (resumen), opcionalmente filtrar por estado
    @GetMapping
    public ResponseEntity<List<PedidoDTO.PedidoResumenResponse>> listarPedidos(
            @RequestParam(required = false) EstadoPedido estado) {

        if (estado != null) {
            return ResponseEntity.ok(pedidoService.listarPorEstado(estado));
        }
        return ResponseEntity.ok(pedidoService.listarPedidos());
    }

    // ── GET /api/pedidos/pendientes ────────────────────────────────────────────
    // Endpoint dedicado para el MS-Orquestador: obtiene pedidos sin asignar
    @GetMapping("/pendientes")
    public ResponseEntity<List<PedidoDTO.PedidoResumenResponse>> listarPendientes() {
        return ResponseEntity.ok(pedidoService.listarPendientes());
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
