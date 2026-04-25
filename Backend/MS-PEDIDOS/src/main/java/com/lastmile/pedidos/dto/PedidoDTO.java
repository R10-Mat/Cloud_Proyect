package com.lastmile.pedidos.dto;

import com.lastmile.pedidos.model.EstadoPedido;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

// ──────────────────────────────────────────────────────────────────────────────
// REQUEST: crear pedido
// ──────────────────────────────────────────────────────────────────────────────
public class PedidoDTO {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class CrearPedidoRequest {

        @NotBlank(message = "El nombre del cliente es obligatorio")
        @Size(max = 100, message = "El nombre no puede superar 100 caracteres")
        private String clienteNombre;

        @NotBlank(message = "El teléfono del cliente es obligatorio")
        @Pattern(regexp = "^[+]?[0-9]{7,15}$", message = "Teléfono inválido")
        private String clienteTelefono;

        @Email(message = "Email inválido")
        private String clienteEmail;

        @NotBlank(message = "La dirección de origen es obligatoria")
        private String direccionOrigen;

        @NotBlank(message = "La dirección de destino es obligatoria")
        private String direccionDestino;

        @NotEmpty(message = "El pedido debe tener al menos un paquete")
        @Valid
        private List<DetallePaqueteDTO.CrearDetalleRequest> paquetes;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // REQUEST: actualizar estado
    // ──────────────────────────────────────────────────────────────────────────
    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ActualizarEstadoRequest {

        @NotNull(message = "El estado es obligatorio")
        private EstadoPedido estado;

        private Long conductorId;   // opcional: lo rellena el orquestador
    }

    // ──────────────────────────────────────────────────────────────────────────
    // RESPONSE: pedido completo
    // ──────────────────────────────────────────────────────────────────────────
    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PedidoResponse {

        private Long id;
        private String clienteNombre;
        private String clienteTelefono;
        private String clienteEmail;
        private String direccionOrigen;
        private String direccionDestino;
        private EstadoPedido estado;
        private Long conductorId;
        private LocalDateTime fechaCreacion;
        private LocalDateTime fechaActualizacion;
        private List<DetallePaqueteDTO.DetalleResponse> paquetes;
    }

    // ──────────────────────────────────────────────────────────────────────────
    // RESPONSE: resumen (para listados)
    // ──────────────────────────────────────────────────────────────────────────
    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PedidoResumenResponse {

        private Long id;
        private String clienteNombre;
        private String direccionDestino;
        private EstadoPedido estado;
        private int cantidadPaquetes;
        private LocalDateTime fechaCreacion;
    }
}
