package com.lastmile.pedidos.controller;

import com.lastmile.pedidos.dto.PedidoDTO;
import com.lastmile.pedidos.model.EstadoPedido;
import com.lastmile.pedidos.service.PedidoService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.util.List;
import java.util.Map;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;

@RestController
@RequestMapping("/api/pedidos")
@RequiredArgsConstructor
@Tag(name = "Pedidos", description = "Gestión de pedidos - Last Mile Delivery")
public class PedidoController {

    private final PedidoService pedidoService;

    // ── POST /api/pedidos ──────────────────────────────────────────────────────
    @PostMapping
    @Operation(
            summary = "Crear un nuevo pedido",
            description = "Registra un nuevo pedido con sus paquetes asociados en el sistema."
    )
    @ApiResponses({
            @ApiResponse(responseCode = "201", description = "Pedido creado exitosamente"),
            @ApiResponse(responseCode = "400", description = "Datos inválidos o incompletos"),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<PedidoDTO.PedidoResponse> crearPedido(
            @Valid @RequestBody PedidoDTO.CrearPedidoRequest request) {

        PedidoDTO.PedidoResponse response = pedidoService.crearPedido(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // ── GET /api/pedidos ───────────────────────────────────────────────────────────
    @GetMapping
    @Operation(
            summary = "Listar pedidos paginados",
            description = "Obtiene un listado paginado de pedidos. Puede filtrar por estado."
    )
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Lista de pedidos"),
            @ApiResponse(responseCode = "400", description = "Parámetros inválidos")
    })
    public ResponseEntity<Map<String, Object>> listarPedidos(
            @Parameter(description = "Filtrar por estado (PENDIENTE, ASIGNADO, EN_CAMINO, ENTREGADO, FALLIDO, CANCELADO)")
            @RequestParam(required = false) EstadoPedido estado,
            @Parameter(description = "Número de página (0-indexed)")
            @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Registros por página (máximo 100)")
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
    @GetMapping("/pendientes")
    @Operation(
            summary = "Listar pedidos pendientes",
            description = "Obtiene pedidos sin asignar (estado PENDIENTE) paginados. Usado por MS-Orquestador."
    )
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Lista de pedidos pendientes"),
            @ApiResponse(responseCode = "400", description = "Parámetros inválidos")
    })
    public ResponseEntity<Map<String, Object>> listarPendientes(
            @Parameter(description = "Número de página (0-indexed)")
            @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Registros por página (máximo 100)")
            @RequestParam(defaultValue = "20") int size) {

        size = Math.max(1, Math.min(100, size));
        page = Math.max(0, page);
        PageRequest pageable = PageRequest.of(page, size);
        return ResponseEntity.ok(pedidoService.listarPendientesPaginado(pageable));
    }

    // ── GET /api/pedidos/{id} ──────────────────────────────────────────────────
    @GetMapping("/{id}")
    @Operation(
            summary = "Obtener detalle de pedido",
            description = "Obtiene información completa de un pedido incluyendo todos sus paquetes."
    )
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Detalle del pedido"),
            @ApiResponse(responseCode = "404", description = "Pedido no encontrado"),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<PedidoDTO.PedidoResponse> obtenerPedido(
            @Parameter(description = "ID del pedido")
            @PathVariable Long id) {
        return ResponseEntity.ok(pedidoService.obtenerPedido(id));
    }

    // ── PATCH /api/pedidos/{id}/estado ─────────────────────────────────────────
    @PatchMapping("/{id}/estado")
    @Operation(
            summary = "Actualizar estado de pedido",
            description = "Cambia el estado del pedido. Usa transiciones de estado validadas."
    )
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Estado actualizado"),
            @ApiResponse(responseCode = "400", description = "Transición de estado inválida"),
            @ApiResponse(responseCode = "404", description = "Pedido no encontrado"),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<PedidoDTO.PedidoResponse> actualizarEstado(
            @Parameter(description = "ID del pedido")
            @PathVariable Long id,
            @Valid @RequestBody PedidoDTO.ActualizarEstadoRequest request) {

        return ResponseEntity.ok(pedidoService.actualizarEstado(id, request));
    }

    // ── DELETE /api/pedidos/{id} ───────────────────────────────────────────────
    @DeleteMapping("/{id}")
    @Operation(
            summary = "Cancelar pedido",
            description = "Cancela un pedido. Solo funciona si está en estado PENDIENTE o ASIGNADO."
    )
    @ApiResponses({
            @ApiResponse(responseCode = "204", description = "Pedido cancelado exitosamente"),
            @ApiResponse(responseCode = "400", description = "Pedido no puede ser cancelado en su estado actual"),
            @ApiResponse(responseCode = "404", description = "Pedido no encontrado"),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<Void> cancelarPedido(
            @Parameter(description = "ID del pedido")
            @PathVariable Long id) {
        pedidoService.cancelarPedido(id);
        return ResponseEntity.noContent().build();
    }

    // ── GET /api/pedidos/health ────────────────────────────────────────────────
    @GetMapping("/health")
    @Operation(summary = "Verificar salud del servicio")
    @ApiResponse(responseCode = "200", description = "Servicio funcionando correctamente")
    public ResponseEntity<Object> health() {
        return ResponseEntity.ok(java.util.Map.of("status", "ok", "service", "ms-pedidos"));
    }
}
