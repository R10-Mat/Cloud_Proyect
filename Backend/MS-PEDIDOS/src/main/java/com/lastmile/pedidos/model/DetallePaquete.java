package com.lastmile.pedidos.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "detalle_paquetes")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DetallePaquete {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // ── Datos del paquete ──────────────────────────────────────────────────────
    @Column(nullable = false, length = 150)
    private String descripcion;

    @Column(name = "peso_kg", nullable = false)
    private Double pesoKg;

    @Column(name = "largo_cm")
    private Double largoCm;

    @Column(name = "ancho_cm")
    private Double anchoCm;

    @Column(name = "alto_cm")
    private Double altoCm;

    @Column(length = 50)
    private String fragil;          // "SI" / "NO"

    @Column(name = "instrucciones_entrega", length = 500)
    private String instruccionesEntrega;

    // ── Relación con el pedido padre ───────────────────────────────────────────
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "pedido_id", nullable = false)
    private Pedido pedido;
}
