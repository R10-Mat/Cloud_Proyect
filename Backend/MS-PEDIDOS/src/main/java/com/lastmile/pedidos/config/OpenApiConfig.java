package com.lastmile.pedidos.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuración de OpenAPI/Swagger para MS-PEDIDOS.
 * Define metadatos y personalización de la documentación API.
 */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("MS-PEDIDOS API")
                        .version("1.0.0")
                        .description("Microservicio de gestión de pedidos - Last Mile Delivery")
                        .contact(new Contact()
                                .name("Last Mile Team")
                                .url("https://lastmile.delivery")
                        )
                );
    }
}
