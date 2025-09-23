        # ==============================
        # Botão para download em Excel formatado (openpyxl)
        # ==============================
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            resultado_pd.to_excel(writer, index=False, sheet_name="Resultados")
            worksheet = writer.sheets["Resultados"]

            # Ajusta largura das colunas automaticamente
            for col in worksheet.columns:
                max_length = 0
                col_name = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = max_length + 2
                worksheet.column_dimensions[col_name].width = adjusted_width

        output.seek(0)

        st.download_button(
            label="📥 Baixar resultado em Excel",
            data=output,
            file_name="resultado_codigos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
