package com.lastmile.pedidos.config;

import com.lastmile.pedidos.dto.DetallePaqueteDTO;
import com.lastmile.pedidos.dto.PedidoDTO;
import com.lastmile.pedidos.model.DetallePaquete;
import com.lastmile.pedidos.model.Pedido;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;


@Component
public class PedidoMapper {

    public PedidoDTO.PedidoResponse toResponse(Pedido pedido) {
        return PedidoDTO.PedidoResponse.builder()
                .id(pedido.getId())
                .clienteNombre(pedido.getClienteNombre())
                .clienteTelefono(pedido.getClienteTelefono())
                .clienteEmail(pedido.getClienteEmail())
                .direccionOrigen(pedido.getDireccionOrigen())
                .direccionDestino(pedido.getDireccionDestino())
                .estado(pedido.getEstado())
                .conductorId(pedido.getConductorId())
                .fechaCreacion(pedido.getFechaCreacion())
                .fechaActualizacion(pedido.getFechaActualizacion())
                .paquetes(toDetalleResponseList(pedido.getPaquetes()))
                .build();
    }

    public PedidoDTO.PedidoResumenResponse toResumen(Pedido pedido) {
        return PedidoDTO.PedidoResumenResponse.builder()
                .id(pedido.getId())
                .clienteNombre(pedido.getClienteNombre())
                .direccionDestino(pedido.getDireccionDestino())
                .estado(pedido.getEstado())
                .cantidadPaquetes(pedido.getPaquetes().size())
                .fechaCreacion(pedido.getFechaCreacion())
                .build();
    }

    public Pedido toEntity(PedidoDTO.CrearPedidoRequest request) {
        Pedido pedido = Pedido.builder()
                .clienteNombre(request.getClienteNombre())
                .clienteTelefono(request.getClienteTelefono())
                .clienteEmail(request.getClienteEmail())
                .direccionOrigen(request.getDireccionOrigen())
                .direccionDestino(request.getDireccionDestino())
                .build();

        request.getPaquetes().stream()
                .map(this::toDetalleEntity)
                .forEach(pedido::agregarPaquete);

        return pedido;
    }

    private DetallePaquete toDetalleEntity(DetallePaqueteDTO.CrearDetalleRequest req) {
        return DetallePaquete.builder()
                .descripcion(req.getDescripcion())
                .pesoKg(req.getPesoKg())
                .largoCm(req.getLargoCm())
                .anchoCm(req.getAnchoCm())
                .altoCm(req.getAltoCm())
                .fragil(req.getFragil())
                .instruccionesEntrega(req.getInstruccionesEntrega())
                .build();
    }

    private DetallePaqueteDTO.DetalleResponse toDetalleResponse(DetallePaquete d) {
        return DetallePaqueteDTO.DetalleResponse.builder()
                .id(d.getId())
                .descripcion(d.getDescripcion())
                .pesoKg(d.getPesoKg())
                .largoCm(d.getLargoCm())
                .anchoCm(d.getAnchoCm())
                .altoCm(d.getAltoCm())
                .fragil(d.getFragil())
                .instruccionesEntrega(d.getInstruccionesEntrega())
                .build();
    }

    private List<DetallePaqueteDTO.DetalleResponse> toDetalleResponseList(List<DetallePaquete> lista) {
        return lista.stream()
                .map(this::toDetalleResponse)
                .collect(Collectors.toList());
    }
}
