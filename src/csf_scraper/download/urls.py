"""URLs del portal del SAT usadas por el módulo de descarga de la CSF.

Todas las URLs viven en este módulo, como ``Url`` en
``phpcfdi/csf-sat-scraper``: ningún servicio las escribe como literales.
"""

LOGIN_BASE_URL = "https://login.siat.sat.gob.mx"
LOGIN_FIEL_SSO_URL = f"{LOGIN_BASE_URL}/nidp/idff/sso?id=fiel_Aviso"
LOGIN_URL = f"{LOGIN_BASE_URL}/nidp/app/login"
LOGOUT_URL = f"{LOGIN_BASE_URL}/nidp/app/logout"

SAML_SSO_URL = f"{LOGIN_BASE_URL}/nidp/saml2/sso"

RFCAMPC_BASE_URL = "https://rfcampc.siat.sat.gob.mx"
SESSION_BROKER_URL = (
    f"{RFCAMPC_BASE_URL}/app/seg/SessionBroker"
    "?url=/PTSC/IdcSiat/autc/ReimpresionTramite/ConsultaTramite.jsf"
    "&parametro=c&idSessionBit=&idSessionBit=null"
)
SAML_ACS_URL = f"{RFCAMPC_BASE_URL}/saml2/sp/acs/post"
CONSULTA_TRAMITE_URL = (
    f"{RFCAMPC_BASE_URL}/PTSC/IdcSiat/autc/ReimpresionTramite/ConsultaTramite.jsf"
)
CONSTANCIA_PDF_URL = f"{RFCAMPC_BASE_URL}/PTSC/IdcSiat/IdcGeneraConstancia.jsf"
