class PredictionResult(Base):
    __tablename__ = 'prediction_results'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_entry_id = Column(UUID(as_uuid=True), ForeignKey('stock_entries.id'), nullable=False)
    prediction_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stock_entry = relationship('StockEntry', backref='predictions')
