# load_tarot_cards.py
import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Importar después de configurar Django
from api.models import CartaTarot

# Datos de las cartas
TAROT_CARDS = [
    {
        "nombre": "El Loco",
        "numero": 0,
        "imagen_nombre": "el_loco.jpg",
        "significado_normal": "Nuevos comienzos, espontaneidad, fe, aparente insensatez. El Loco representa el inicio de un viaje, tomando riesgos y abriéndose a nuevas posibilidades. Indica libertad, idealismo y un espíritu de aventura.",
        "significado_invertido": "Imprudencia, descuido, apatía, inmadurez. La carta invertida sugiere decisiones precipitadas, potencial para desastres, negligencia o acciones sin pensar en las consecuencias."
    },
    {
        "nombre": "El Mago",
        "numero": 1,
        "imagen_nombre": "el_mago.jpg",
        "significado_normal": "Poder, habilidad, concentración, acción, determinación. El Mago representa tu capacidad para manifestar tus deseos mediante voluntad y concentración. Indica creatividad, ingenio y el comienzo de algo nuevo.",
        "significado_invertido": "Manipulación, engaños, inseguridad, uso indebido de poder. La carta invertida sugiere objetivos confusos, charlatanería o talento desperdiciado."
    },
    {
        "nombre": "La Sacerdotisa",
        "numero": 2,
        "imagen_nombre": "la_sacerdotisa.jpg",
        "significado_normal": "Intuición, sabiduría inconsciente, conocimiento interno, lo divino femenino. La Sacerdotisa representa el mundo de los sueños, la intuición y el subconsciente. Indica la necesidad de confiar en tu voz interior.",
        "significado_invertido": "Secretos, desconexión de la intuición, información oculta. La carta invertida sugiere una represión de la intuición, verdades sin revelar o malentendidos."
    },
    {
        "nombre": "La Emperatriz",
        "numero": 3,
        "imagen_nombre": "la_emperatriz.jpg",
        "significado_normal": "Abundancia, fertilidad, maternidad, creatividad, naturaleza. La Emperatriz representa la energía femenina creativa y nutricia. Indica crecimiento, prosperidad y la manifestación física de las ideas.",
        "significado_invertido": "Dependencia, sobreprotección, problemas creativos, negligencia. La carta invertida sugiere bloqueos creativos, abandono de proyectos o excesiva indulgencia."
    },
    {
        "nombre": "El Emperador",
        "numero": 4,
        "imagen_nombre": "el_emperador.jpg",
        "significado_normal": "Autoridad, estructura, control, liderazgo, estabilidad. El Emperador representa el poder masculino, la figura paterna y la autoridad. Indica disciplina, orden y la capacidad de liderar con firmeza.",
        "significado_invertido": "Dominación, rigidez, inflexibilidad, pérdida de control. La carta invertida sugiere tiranía, obstinación o impotencia frente a desafíos de autoridad."
    },
    {
        "nombre": "El Sumo Sacerdote",
        "numero": 5,
        "imagen_nombre": "el_sumo_sacerdote.jpg",
        "significado_normal": "Tradición, conformidad, moralidad, creencias. El Sumo Sacerdote representa la conexión con lo divino a través de rituales y conocimiento establecido. Indica orientación espiritual y respeto por las instituciones.",
        "significado_invertido": "Rebeldía, subversión, nuevas ideas, desconfianza en las instituciones. La carta invertida sugiere cuestionamiento de dogmas, no conformidad o espiritualidad personal."
    },
    {
        "nombre": "Los Enamorados",
        "numero": 6,
        "imagen_nombre": "los_enamorados.jpg",
        "significado_normal": "Amor, armonía, relaciones, valores, elecciones. Los Enamorados representan conexiones profundas y decisiones del corazón. Indica alianzas, atracciones y momentos cruciales de elección.",
        "significado_invertido": "Desequilibrio, desalineación, valores conflictivos. La carta invertida sugiere desacuerdos en relaciones, decisiones equivocadas basadas en la lujuria o temor al compromiso."
    },
    {
        "nombre": "El Carro",
        "numero": 7,
        "imagen_nombre": "el_carro.jpg",
        "significado_normal": "Control, voluntad, victoria, determinación, avance. El Carro representa la capacidad de superar obstáculos mediante confianza y control. Indica progreso, momentum y triunfo sobre la adversidad.",
        "significado_invertido": "Falta de dirección, agresión, obstáculos insuperables. La carta invertida sugiere fracaso debido a la falta de enfoque, conflictos sin resolución o derrotas."
    },
    {
        "nombre": "La Fuerza",
        "numero": 8,
        "imagen_nombre": "la_fuerza.jpg",
        "significado_normal": "Coraje, persuasión, influencia, energía, determinación. La Fuerza representa el poder de la compasión y la paciencia frente a los impulsos salvajes. Indica control interior, valentía y perseverancia.",
        "significado_invertido": "Debilidad, cobardía, falta de autocontrol. La carta invertida sugiere dominio por los impulsos primitivos, abuso de poder o dudas paralizantes."
    },
    {
        "nombre": "El Ermitaño",
        "numero": 9,
        "imagen_nombre": "el_ermitaño.jpg",
        "significado_normal": "Introspección, búsqueda, soledad, orientación interior. El Ermitaño representa el retiro voluntario para contemplación y autoconocimiento. Indica sabiduría, prudencia y la búsqueda de verdades más profundas.",
        "significado_invertido": "Aislamiento, soledad, rechazo al consejo. La carta invertida sugiere excesivo aislamiento, paranoia o negación a compartir conocimientos."
    },
    {
        "nombre": "La Rueda de la Fortuna",
        "numero": 10,
        "imagen_nombre": "la_rueda_de_la_fortuna.jpg",
        "significado_normal": "Destino, suerte, ciclos, punto de inflexión, karma. La Rueda de la Fortuna representa los giros inesperados y los ciclos inevitables de la vida. Indica cambios, oportunidades y fuerzas más allá de nuestro control.",
        "significado_invertido": "Interrupción, reveses, mala suerte. La carta invertida sugiere resistencia al cambio, adversidades o consecuencias negativas de decisiones pasadas."
    },
    {
        "nombre": "La Justicia",
        "numero": 11,
        "imagen_nombre": "la_justicia.jpg",
        "significado_normal": "Justicia, equilibrio, verdad, ley, claridad. La Justicia representa la imparcialidad y las consecuencias de nuestras acciones. Indica honestidad, responsabilidad y decisiones equilibradas.",
        "significado_invertido": "Injusticia, parcialidad, deshonestidad. La carta invertida sugiere desequilibrio, decisiones legales desfavorables o manipulación de la verdad."
    },
    {
        "nombre": "El Colgado",
        "numero": 12,
        "imagen_nombre": "el_colgado.jpg",
        "significado_normal": "Rendición, nuevas perspectivas, suspensión, sacrificio. El Colgado representa el poder de soltar y ver las cosas de manera diferente. Indica transición, paciencia y sabiduría a través del sacrificio.",
        "significado_invertido": "Estancamiento, resistencia, indecisión. La carta invertida sugiere incapacidad para dejar el pasado atrás, sacrificios inútiles o resistencia a nuevas perspectivas."
    },
    {
        "nombre": "La Muerte",
        "numero": 13,
        "imagen_nombre": "la_muerte.jpg",
        "significado_normal": "Fin, cambio, transformación, transición. La Muerte representa finales necesarios y renacimientos. Indica cambios profundos, liberación de lo viejo y oportunidades para un nuevo comienzo.",
        "significado_invertido": "Resistencia al cambio, estancamiento, incapacidad para seguir adelante. La carta invertida sugiere aferrarse al pasado, miedo a lo desconocido o cambios parciales."
    },
    {
        "nombre": "La Templanza",
        "numero": 14,
        "imagen_nombre": "la_templanza.jpg",
        "significado_normal": "Equilibrio, moderación, paciencia, propósito. La Templanza representa la armonización de fuerzas opuestas y la unificación. Indica serenidad, autocontrol y la capacidad de encontrar el punto medio.",
        "significado_invertido": "Desequilibrio, excesos, conflictos internos. La carta invertida sugiere desalineación, impulsividad o falta de visión a largo plazo."
    },
    {
        "nombre": "El Diablo",
        "numero": 15,
        "imagen_nombre": "el_diablo.jpg",
        "significado_normal": "Materialismo, tentación, ataduras, sexualidad. El Diablo representa las ataduras autoimpuestas y la influencia de los deseos materiales. Indica adicciones, dependencias y la ilusión de estar atrapado.",
        "significado_invertido": "Liberación, independencia, enfrentamiento de miedos. La carta invertida sugiere romper cadenas, confrontar la oscuridad interior o recuperar el control."
    },
    {
        "nombre": "La Torre",
        "numero": 16,
        "imagen_nombre": "la_torre.jpg",
        "significado_normal": "Desastre repentino, revelación, despertar, liberación. La Torre representa cambios bruscos y colapsos necesarios. Indica destrucción de falsas estructuras, verdades chocantes y liberación a través del caos.",
        "significado_invertido": "Crisis evitada, resistir el cambio, prolongación del sufrimiento. La carta invertida sugiere negación de problemas evidentes, miedo a la destrucción o cambios menos dramáticos."
    },
    {
        "nombre": "La Estrella",
        "numero": 17,
        "imagen_nombre": "la_estrella.jpg",
        "significado_normal": "Esperanza, fe, propósito, renovación, espiritualidad. La Estrella representa la inspiración divina y el consuelo después de tiempos difíciles. Indica optimismo, generosidad y conexión con lo universal.",
        "significado_invertido": "Desesperanza, desánimo, falta de fe. La carta invertida sugiere pérdida de fe, desilusión o sentimientos de abandono espiritual."
    },
    {
        "nombre": "La Luna",
        "numero": 18,
        "imagen_nombre": "la_luna.jpg",
        "significado_normal": "Ilusión, temores, incertidumbre, subconsciente, intuición. La Luna representa el mundo de sueños y sombras. Indica ambigüedad, intuición profunda, emociones ocultas y el viaje a través de lo desconocido.",
        "significado_invertido": "Confusión, miedo, malentendidos. La carta invertida sugiere engaño, mente perturbada o incapacidad para discernir la realidad."
    },
    {
        "nombre": "El Sol",
        "numero": 19,
        "imagen_nombre": "el_sol.jpg",
        "significado_normal": "Alegría, éxito, celebración, positividad, vitalidad. El Sol representa la claridad y el logro. Indica iluminación, verdad, optimismo y la capacidad de brillar en todo tu potencial.",
        "significado_invertido": "Excesivo optimismo, desilusión, claridad temporal. La carta invertida sugiere éxito postergado, exceso de confianza o felicidad superficial."
    },
    {
        "nombre": "El Juicio",
        "numero": 20,
        "imagen_nombre": "el_juicio.jpg",
        "significado_normal": "Juicio, renacimiento, renovación interna, despertar. El Juicio representa el llamado a una vida nueva y el reconocimiento de tu verdadero propósito. Indica autoevaluación, absolución y transformación profunda.",
        "significado_invertido": "Falta de autoconocimiento, negación, dudas sobre uno mismo. La carta invertida sugiere resistencia al llamado interior, remordimiento o incapacidad para aprender de experiencias pasadas."
    },
    {
        "nombre": "El Mundo",
        "numero": 21,
        "imagen_nombre": "el_mundo.jpg",
        "significado_normal": "Realización, integración, logro, cumplimiento. El Mundo representa la finalización exitosa de un ciclo y la armonía. Indica plenitud, éxito, integración de todas las partes y el sentido de totalidad.",
        "significado_invertido": "Incompleto, atascado, falta de clausura. La carta invertida sugiere demoras en completar ciclos, estancamiento o incapacidad para integrarse plenamente."
    }
]

def load_cards():
    # Limpiar base de datos existente (opcional)
    CartaTarot.objects.all().delete()
    
    # Cargar nuevas cartas
    for card_data in TAROT_CARDS:
        CartaTarot.objects.create(**card_data)
        print(f"Carta creada: {card_data['nombre']}")
    
    print(f"Total de cartas cargadas: {CartaTarot.objects.count()}")

if __name__ == "__main__":
    load_cards()