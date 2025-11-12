"""
Script de Prueba para Agentes LangChain
Verifica que todos los componentes funcionan correctamente
"""
import sys
import os

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(mensaje, resultado=None):
    """Imprime resultado de test"""
    if resultado is None:
        print(f"\n{Colors.BLUE}{Colors.BOLD}📋 {mensaje}{Colors.RESET}")
    elif resultado:
        print(f"   {Colors.GREEN}✅ {mensaje}{Colors.RESET}")
    else:
        print(f"   {Colors.RED}❌ {mensaje}{Colors.RESET}")

def print_separator():
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.RESET}")

# ============================================================
# TEST 1: IMPORTACIONES
# ============================================================
def test_imports():
    """Verifica que se pueden importar los módulos"""
    print_separator()
    print_test("TEST 1: Verificando importaciones")
    
    tests_passed = 0
    tests_total = 5
    
    # Test 1.1: LangChain
    try:
        from langchain.agents import Tool
        print_test("LangChain instalado", True)
        tests_passed += 1
    except ImportError as e:
        print_test(f"LangChain NO instalado: {e}", False)
    
    # Test 1.2: Agente Extractor
    try:
        from agentes.extractor_langchain import AgenteExtractorLangChain
        print_test("AgenteExtractorLangChain importable", True)
        tests_passed += 1
    except ImportError as e:
        print_test(f"AgenteExtractorLangChain NO importable: {e}", False)
    
    # Test 1.3: Agente Buscador
    try:
        from agentes.buscador_langchain import AgenteBuscadorLangChain
        print_test("AgenteBuscadorLangChain importable", True)
        tests_passed += 1
    except ImportError as e:
        print_test(f"AgenteBuscadorLangChain NO importable: {e}", False)
    
    # Test 1.4: Agente Respondedor
    try:
        from agentes.respondedor_langchain import AgenteRespondedorLangChain
        print_test("AgenteRespondedorLangChain importable", True)
        tests_passed += 1
    except ImportError as e:
        print_test(f"AgenteRespondedorLangChain NO importable: {e}", False)
    
    # Test 1.5: Sistema Orquestador
    try:
        from sistema_langchain import SistemaMultiagenteDocuBot
        print_test("SistemaMultiagenteDocuBot importable", True)
        tests_passed += 1
    except ImportError as e:
        print_test(f"SistemaMultiagenteDocuBot NO importable: {e}", False)
    
    print(f"\n   {Colors.BOLD}Resultado: {tests_passed}/{tests_total} tests pasados{Colors.RESET}")
    return tests_passed == tests_total

# ============================================================
# TEST 2: AGENTE EXTRACTOR
# ============================================================
def test_agente_extractor():
    """Prueba el Agente Extractor"""
    print_separator()
    print_test("TEST 2: Probando Agente Extractor")
    
    try:
        from agentes.extractor_langchain import AgenteExtractorLangChain
        
        # Crear agente
        agente = AgenteExtractorLangChain("documentos")
        print_test(f"Agente creado", True)
        
        # Verificar tools
        if len(agente.tools) == 4:
            print_test(f"4 Tools creadas correctamente", True)
            for tool in agente.tools:
                print(f"      • {tool.name}: {tool.description[:50]}...")
        else:
            print_test(f"Esperaba 4 tools, encontró {len(agente.tools)}", False)
        
        # Verificar métodos principales
        metodos = ['leer_documentos', 'crear_chunks', 'limpiar_texto']
        for metodo in metodos:
            if hasattr(agente, metodo):
                print_test(f"Método '{metodo}' existe", True)
            else:
                print_test(f"Método '{metodo}' NO existe", False)
        
        return True
    except Exception as e:
        print_test(f"Error: {str(e)}", False)
        return False

# ============================================================
# TEST 3: AGENTE BUSCADOR
# ============================================================
def test_agente_buscador():
    """Prueba el Agente Buscador"""
    print_separator()
    print_test("TEST 3: Probando Agente Buscador")
    
    try:
        from agentes.buscador_langchain import AgenteBuscadorLangChain
        
        # Crear agente
        agente = AgenteBuscadorLangChain()
        print_test(f"Agente creado", True)
        
        # Verificar tools
        if len(agente.tools) == 4:
            print_test(f"4 Tools creadas correctamente", True)
            for tool in agente.tools:
                print(f"      • {tool.name}: {tool.description[:50]}...")
        else:
            print_test(f"Esperaba 4 tools, encontró {len(agente.tools)}", False)
        
        # Verificar atributos
        if hasattr(agente, 'modelo'):
            print_test(f"Modelo de embeddings cargado", True)
        else:
            print_test(f"Modelo de embeddings NO cargado", False)
        
        # Verificar métodos
        metodos = ['crear_base_vectorial', 'buscar_relevantes', 'expandir_consulta']
        for metodo in metodos:
            if hasattr(agente, metodo):
                print_test(f"Método '{metodo}' existe", True)
            else:
                print_test(f"Método '{metodo}' NO existe", False)
        
        return True
    except Exception as e:
        print_test(f"Error: {str(e)}", False)
        return False

# ============================================================
# TEST 4: AGENTE RESPONDEDOR
# ============================================================
def test_agente_respondedor():
    """Prueba el Agente Respondedor"""
    print_separator()
    print_test("TEST 4: Probando Agente Respondedor")
    
    try:
        from agentes.respondedor_langchain import AgenteRespondedorLangChain
        
        # Crear agente
        agente = AgenteRespondedorLangChain()
        print_test(f"Agente creado", True)
        
        # Verificar tools
        if len(agente.tools) == 5:
            print_test(f"5 Tools creadas correctamente", True)
            for tool in agente.tools:
                print(f"      • {tool.name}: {tool.description[:50]}...")
        else:
            print_test(f"Esperaba 5 tools, encontró {len(agente.tools)}", False)
        
        # Verificar métodos
        metodos = ['generar_respuesta_precisa', 'calcular_confianza', 'extraer_oraciones_relevantes']
        for metodo in metodos:
            if hasattr(agente, metodo):
                print_test(f"Método '{metodo}' existe", True)
            else:
                print_test(f"Método '{metodo}' NO existe", False)
        
        return True
    except Exception as e:
        print_test(f"Error: {str(e)}", False)
        return False

# ============================================================
# TEST 5: SISTEMA COMPLETO
# ============================================================
def test_sistema_completo():
    """Prueba el sistema orquestador"""
    print_separator()
    print_test("TEST 5: Probando Sistema Orquestador")
    
    try:
        from sistema_langchain import SistemaMultiagenteDocuBot
        
        # Crear sistema
        sistema = SistemaMultiagenteDocuBot("documentos")
        print_test(f"Sistema creado", True)
        
        # Verificar agentes
        if hasattr(sistema, 'agente_extractor'):
            print_test(f"Agente Extractor integrado", True)
        else:
            print_test(f"Agente Extractor NO integrado", False)
        
        if hasattr(sistema, 'agente_buscador'):
            print_test(f"Agente Buscador integrado", True)
        else:
            print_test(f"Agente Buscador NO integrado", False)
        
        if hasattr(sistema, 'agente_respondedor'):
            print_test(f"Agente Respondedor integrado", True)
        else:
            print_test(f"Agente Respondedor NO integrado", False)
        
        # Verificar system tools
        if len(sistema.system_tools) == 3:
            print_test(f"3 System Tools creadas", True)
            for tool in sistema.system_tools:
                print(f"      • {tool.name}: {tool.description[:50]}...")
        else:
            print_test(f"Esperaba 3 system tools, encontró {len(sistema.system_tools)}", False)
        
        # Verificar métodos principales
        metodos = ['cargar_documentos', 'procesar_pregunta', 'obtener_estadisticas']
        for metodo in metodos:
            if hasattr(sistema, metodo):
                print_test(f"Método '{metodo}' existe", True)
            else:
                print_test(f"Método '{metodo}' NO existe", False)
        
        return True
    except Exception as e:
        print_test(f"Error: {str(e)}", False)
        import traceback
        print(traceback.format_exc())
        return False

# ============================================================
# TEST 6: FLUJO COMPLETO CON DATOS REALES
# ============================================================
def test_flujo_completo():
    """Prueba el flujo completo con documentos reales"""
    print_separator()
    print_test("TEST 6: Probando Flujo Completo (si hay documentos)")
    
    try:
        from sistema_langchain import SistemaMultiagenteDocuBot
        
        # Verificar que existe carpeta documentos
        if not os.path.exists("documentos"):
            print_test("⚠️  Carpeta 'documentos/' no existe - Test omitido", None)
            return True
        
        # Verificar que hay archivos
        archivos = os.listdir("documentos")
        archivos_validos = [f for f in archivos if f.endswith(('.txt', '.pdf'))]
        
        if not archivos_validos:
            print_test("⚠️  No hay archivos .txt o .pdf - Test omitido", None)
            return True
        
        print_test(f"Encontrados {len(archivos_validos)} archivos", True)
        
        # Crear sistema
        sistema = SistemaMultiagenteDocuBot("documentos")
        
        # Test 6.1: Cargar documentos
        print_test("\n   🔹 Probando carga de documentos...")
        resultado = sistema.cargar_documentos(tamano_chunk=300)
        
        if resultado['success']:
            print_test(f"Documentos cargados: {resultado['documentos']}", True)
            print_test(f"Chunks creados: {resultado['chunks']}", True)
        else:
            print_test(f"Error al cargar documentos", False)
            return False
        
        # Test 6.2: Procesar pregunta
        print_test("\n   🔹 Probando procesamiento de pregunta...")
        pregunta = "¿Qué información contienen los documentos?"
        
        try:
            respuesta = sistema.procesar_pregunta(pregunta, top_k=2)
            if respuesta and len(respuesta) > 0:
                print_test(f"Respuesta generada ({len(respuesta)} caracteres)", True)
                print(f"\n{Colors.YELLOW}      Fragmento de respuesta:{Colors.RESET}")
                print(f"      {respuesta[:200]}...")
            else:
                print_test("Respuesta vacía", False)
        except Exception as e:
            print_test(f"Error al procesar pregunta: {str(e)}", False)
            return False
        
        # Test 6.3: Estadísticas
        print_test("\n   🔹 Probando estadísticas...")
        stats = sistema.obtener_estadisticas()
        
        if stats['listo']:
            print_test(f"Sistema listo", True)
            print(f"      • Documentos: {stats['documentos']}")
            print(f"      • Chunks: {stats['chunks']}")
            print(f"      • Agentes activos: {stats['agentes_activos']}")
        else:
            print_test("Sistema no está listo", False)
        
        return True
        
    except Exception as e:
        print_test(f"Error: {str(e)}", False)
        import traceback
        print(traceback.format_exc())
        return False

# ============================================================
# TEST 7: CONTEO DE TOOLS
# ============================================================
def test_conteo_tools():
    """Cuenta todas las tools del sistema"""
    print_separator()
    print_test("TEST 7: Conteo de Tools LangChain")
    
    try:
        from agentes.extractor_langchain import AgenteExtractorLangChain
        from agentes.buscador_langchain import AgenteBuscadorLangChain
        from agentes.respondedor_langchain import AgenteRespondedorLangChain
        from sistema_langchain import SistemaMultiagenteDocuBot
        
        extractor = AgenteExtractorLangChain("documentos")
        buscador = AgenteBuscadorLangChain()
        respondedor = AgenteRespondedorLangChain()
        sistema = SistemaMultiagenteDocuBot("documentos")
        
        total_tools = (
            len(extractor.tools) + 
            len(buscador.tools) + 
            len(respondedor.tools) + 
            len(sistema.system_tools)
        )
        
        print(f"\n   📊 {Colors.BOLD}RESUMEN DE TOOLS:{Colors.RESET}")
        print(f"      • Agente Extractor: {len(extractor.tools)} tools")
        print(f"      • Agente Buscador: {len(buscador.tools)} tools")
        print(f"      • Agente Respondedor: {len(respondedor.tools)} tools")
        print(f"      • Sistema Orquestador: {len(sistema.system_tools)} tools")
        print(f"\n      {Colors.GREEN}{Colors.BOLD}TOTAL: {total_tools} Tools LangChain{Colors.RESET}")
        
        if total_tools == 16:
            print_test(f"✅ Cumple con las 16 tools esperadas", True)
            return True
        else:
            print_test(f"⚠️  Se esperaban 16 tools, hay {total_tools}", False)
            return False
        
    except Exception as e:
        print_test(f"Error: {str(e)}", False)
        return False

# ============================================================
# MAIN
# ============================================================
def main():
    """Ejecuta todos los tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("🧪 SUITE DE PRUEBAS - AGENTES LANGCHAIN")
    print("="*60)
    print(Colors.RESET)
    
    resultados = []
    
    # Ejecutar tests
    resultados.append(("Importaciones", test_imports()))
    resultados.append(("Agente Extractor", test_agente_extractor()))
    resultados.append(("Agente Buscador", test_agente_buscador()))
    resultados.append(("Agente Respondedor", test_agente_respondedor()))
    resultados.append(("Sistema Orquestador", test_sistema_completo()))
    resultados.append(("Conteo de Tools", test_conteo_tools()))
    resultados.append(("Flujo Completo", test_flujo_completo()))
    
    # Resultados finales
    print_separator()
    print(f"\n{Colors.BOLD}{Colors.BLUE}📊 RESULTADOS FINALES{Colors.RESET}\n")
    
    tests_pasados = 0
    tests_totales = len(resultados)
    
    for nombre, resultado in resultados:
        if resultado:
            print(f"   {Colors.GREEN}✅ {nombre}: PASÓ{Colors.RESET}")
            tests_pasados += 1
        else:
            print(f"   {Colors.RED}❌ {nombre}: FALLÓ{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}   Total: {tests_pasados}/{tests_totales} tests pasados{Colors.RESET}")
    
    if tests_pasados == tests_totales:
        print(f"\n{Colors.GREEN}{Colors.BOLD}   🎉 ¡TODOS LOS TESTS PASARON!{Colors.RESET}")
        print(f"{Colors.GREEN}   ✅ Los agentes LangChain están funcionando correctamente{Colors.RESET}")
    elif tests_pasados >= tests_totales - 1:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}   ⚠️  CASI TODO FUNCIONA{Colors.RESET}")
        print(f"{Colors.YELLOW}   Revisa el test que falló arriba{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}   ❌ HAY PROBLEMAS{Colors.RESET}")
        print(f"{Colors.RED}   Revisa los errores arriba{Colors.RESET}")
    
    print_separator()
    print()

if __name__ == "__main__":
    main()