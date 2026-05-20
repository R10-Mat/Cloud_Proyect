package com.lastmile.pedidos.model;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "pedidos")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Pedido {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // ── Datos del cliente ──────────────────────────────────────────────────────
    @Column(name = "cliente_nombre", nullable = false, length = 100)
    private String clienteNombre;

    @Column(name = "cliente_telefono", nullable = false, length = 20)
    private String clienteTelefono;

    @Column(name = "cliente_email", length = 100)
    private String clienteEmail;

    // ── Direcciones ────────────────────────────────────────────────────────────
    @Column(name = "direccion_origen", nullable = false, length = 255)
    private String direccionOrigen;

    @Column(name = "direccion_destino", nullable = false, length = 255)
    private String direccionDestino;

    // ── Estado del pedido ──────────────────────────────────────────────────────
    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    @Builder.Default
    private EstadoPedido estado = EstadoPedido.PENDIENTE;

    // ── Asignación ─────────────────────────────────────────────────────────────
    // Se llenará cuando el MS-Orquestador asigne un conductor
    @Column(name = "conductor_id")
    private Long conductorId;

    // ── Timestamps ─────────────────────────────────────────────────────────────
    @CreationTimestamp
    @Column(name = "fecha_creacion", updatable = false)
    private LocalDateTime fechaCreacion;

    @UpdateTimestamp
    @Column(name = "fecha_actualizacion")
    private LocalDateTime fechaActualizacion;

    @OneToMany(
        mappedBy = "pedido",
        cascade = CascadeType.ALL,
        orphanRemoval = true,
        fetch = FetchType.LAZY
    )
    @Builder.Default
    private List<DetallePaquete> paquetes = new ArrayList<>();

    public void agregarPaquete(DetallePaquete paquete) {
        paquetes.add(paquete);
        paquete.setPedido(this);
    }

    public void removerPaquete(DetallePaquete paquete) {
        paquetes.remove(paquete);
        paquete.setPedido(null);
    }
}
