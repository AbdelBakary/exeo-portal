# EXEO Security Portal

Portail web multi-locataire pour la gestion de la cybersécurité développé pour EXEO.

## 🚀 Fonctionnalités

### Tableau de bord interactif
- Visualisation en temps réel des alertes de sécurité
- Graphiques de répartition par type, sévérité et évolution temporelle
- Distribution des scores de risque
- Métriques de performance et indicateurs clés

### Gestion des alertes
- Système d'alertes multi-locataire avec séparation stricte des données
- Classification automatique par sévérité et type
- Assignation et suivi des alertes
- Commentaires et pièces jointes
- Règles de filtrage personnalisées

### Intelligence sur les menaces (Threat Intelligence)
- Agrégation de sources multiples (MISP, CERT-FR, OSINT)
- Corrélation automatique avec les alertes existantes
- Classification des indicateurs de compromission (IOC)
- Rapports de menaces automatisés

### Automatisation SOAR
- Playbooks configurables pour l'automatisation des réponses
- Intégration avec les systèmes externes (pare-feu, SIEM, etc.)
- Règles d'escalade automatique
- Actions automatisées (blocage IP, création de tickets, notifications)

### Moteur de scoring IA
- Calcul automatique des scores de risque (0-10)
- Modèles de machine learning avec scikit-learn
- Facteurs de risque multiples (sévérité, contexte, fréquence)
- Amélioration continue des modèles

### Rapports et analytics
- Génération de rapports PDF/CSV
- Tableaux de bord personnalisables
- Métriques de performance
- Export de données

## 🏗️ Architecture

### Backend (Django)
- **Framework**: Django 4.2 + Django REST Framework
- **Base de données**: PostgreSQL
- **Cache**: Redis
- **Queue**: Celery
- **Authentification**: JWT avec multi-facteur
- **API**: REST avec pagination et filtrage

### Frontend (React)
- **Framework**: React 18
- **Routing**: React Router
- **State Management**: React Query
- **UI**: Composants personnalisés avec Tailwind CSS
- **Charts**: Chart.js + React-Chartjs-2

### Infrastructure
- **Conteneurisation**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Monitoring**: Health checks intégrés
- **Sécurité**: HTTPS, headers de sécurité, rate limiting

## 🚀 Installation et déploiement

### Prérequis
- Docker et Docker Compose
- Git

### Installation rapide

1. **Cloner le repository**
```bash
git clone <repository-url>
cd exeo-portal
```

2. **Configurer l'environnement**
```bash
cp env.example .env
# Éditer .env avec vos paramètres
```

3. **Démarrer les services**
```bash
docker-compose up -d
```

4. **Initialiser la base de données**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python scripts/create_superuser.py
docker-compose exec web python scripts/generate_sample_data.py
```

5. **Accéder à l'application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Django: http://localhost:8000/admin

### Comptes de démonstration
- **Admin**: admin@exeo.com / admin123
- **Analyste SOC**: analyst@exeo.com / analyst123
- **Client**: client@exeo.com / client123

## 📁 Structure du projet

```
exeo-portal/
├── apps/                          # Applications Django
│   ├── accounts/                  # Gestion des utilisateurs et clients
│   ├── alerts/                    # Gestion des alertes
│   ├── incidents/                 # Gestion des incidents
│   ├── threat_intelligence/       # Threat Intelligence
│   ├── soar/                      # Automatisation SOAR
│   ├── analytics/                 # Analytics et ML
│   └── reports/                   # Rapports
├── frontend/                      # Application React
│   ├── src/
│   │   ├── components/            # Composants réutilisables
│   │   ├── pages/                 # Pages de l'application
│   │   ├── services/              # Services API
│   │   └── hooks/                 # Hooks personnalisés
│   └── public/
├── scripts/                       # Scripts utilitaires
├── docker-compose.yml            # Configuration Docker Compose
├── Dockerfile                     # Image Docker backend
└── requirements.txt              # Dépendances Python
```

## 🔧 Configuration

### Variables d'environnement

Copiez `env.example` vers `.env` et configurez :

```bash
# Base de données
DATABASE_URL=postgresql://exeo_user:exeo_password@db:5432/exeo_portal

# Sécurité
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis
REDIS_URL=redis://redis:6379/0

# APIs externes
MISP_URL=https://your-misp-instance.com
MISP_API_KEY=your-misp-api-key
CERT_FR_API_KEY=your-cert-fr-api-key

# SOAR
FIREWALL_API_URL=https://your-firewall-api.com
FIREWALL_API_KEY=your-firewall-api-key
```

### Configuration des intégrations

1. **MISP**: Configurez l'URL et la clé API de votre instance MISP
2. **CERT-FR**: Ajoutez votre clé API CERT-FR
3. **Pare-feu**: Configurez l'API de votre pare-feu pour les actions SOAR

## 🧪 Tests

### Tests backend
```bash
docker-compose exec web python manage.py test
```

### Tests frontend
```bash
docker-compose exec frontend npm test
```

## 📊 Monitoring et logs

### Logs
- **Application**: `docker-compose logs web`
- **Base de données**: `docker-compose logs db`
- **Redis**: `docker-compose logs redis`

### Health checks
- Backend: http://localhost:8000/health/
- Frontend: http://localhost:3000

## 🔒 Sécurité

### Mesures implémentées
- Authentification JWT avec expiration
- Séparation stricte des données par client
- Headers de sécurité (HSTS, XSS Protection, etc.)
- Rate limiting sur les APIs
- Validation des entrées utilisateur
- Chiffrement des mots de passe
- Audit logs complets

### Recommandations de production
- Utiliser HTTPS en production
- Configurer des certificats SSL valides
- Mettre à jour les clés secrètes
- Configurer la sauvegarde de la base de données
- Monitorer les logs de sécurité

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou support :
- Email: support@exeo.com
- Documentation: [Lien vers la documentation]
- Issues: [Lien vers les issues GitHub]

## 🗺️ Roadmap

### Version 1.1
- [ ] Interface mobile optimisée
- [ ] Notifications push
- [ ] Intégration Slack/Teams
- [ ] API GraphQL

### Version 1.2
- [ ] Machine Learning avancé
- [ ] Détection d'anomalies
- [ ] Corrélation temporelle
- [ ] Tableaux de bord personnalisables

### Version 2.0
- [ ] Multi-tenant avancé
- [ ] API publique
- [ ] Intégrations tierces
- [ ] Analytics prédictives
