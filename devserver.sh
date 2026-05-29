echo "---- Dependencias do Projeto Python ----"
pip install -r requirements.txt
echo "---- Dependencias do Projeto Node.js ----"
npm install -g firebase-tools
echo "---- Projeto Pronto para Uso ----"
echo ""
for i in {5.1}; do
    echo -ne "Servidor será iniciado em ${i} segundos... \r "
    sleep 1
done
clear
py app.py