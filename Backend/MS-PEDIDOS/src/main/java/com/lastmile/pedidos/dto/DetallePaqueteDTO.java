package com.lastmile.pedidos.dto;

import jakarta.validation.constraints.*;
import lombok.*;

public class DetallePaqueteDTO {

    
    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class CrearDetalleRequest {

        @NotBlank(message = "La descripción del paquete es obligatoria")
        @Size(max = 150, message = "La descripción no puede superar 150 caracteres")
        private String descripcion;

        @NotNull(message = "El peso es obligatorio")
        @DecimalMin(value = "0.01", message = "El peso debe ser mayor a 0")
        @DecimalMax(value = "500.0", message = "El peso no puede superar 500 kg")
        private Double pesoKg;

        @DecimalMin(value = "0.0", message = "El largo debe ser positivo")
        private Double largoCm;

        @DecimalMin(value = "0.0", message = "El ancho debe ser positivo")
        private Double anchoCm;

        @DecimalMin(value = "0.0", message = "El alto debe ser positivo")
        private Double altoCm;

        private String fragil;

        @Size(max = 500, message = "Las instrucciones no pueden superar 500 caracteres")
        private String instruccionesEntrega;
    }

    
    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DetalleResponse {

        private Long id;
        private String descripcion;
        private Double pesoKg;
        private Double largoCm;
        private Double anchoCm;
        private Double altoCm;
        private String fragil;
        private String instruccionesEntrega;
    }
}
