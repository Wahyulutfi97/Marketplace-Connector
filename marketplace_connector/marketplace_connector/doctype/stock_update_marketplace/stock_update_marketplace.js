// // Copyright (c) 2021, PT DAS and contributors
// // For license information, please see license.txt

// frappe.ui.form.on('Stock Update Marketplace', {
// 	refresh: function(frm) {
// 		// frm.set_query('item_code_2', 'items', function(doc, cdt, cdn) {
// 		// 	var d = locals[cdt][cdn];
// 		// 	return {
// 		// 		"filters": {
// 		// 			"item_group": "Shopee"
// 		// 		}
// 		// 	};
// 		// });
// 		frm.set_query('item', 'item_stock_tokopedia', function(doc, cdt, cdn) {
// 			var d = locals[cdt][cdn];
// 			return {
// 				"filters": {
// 					"item_group": cur_frm.doc.tokopedia_toko + " Tokopedia"
// 				}
// 			};
// 		});
// 		// if (cur_frm.doc.docstatus == 0) {
// 		// 	cur_frm.set_value('posting_time', moment(frappe.datetime.now_datetime()).format("HH:mm:ss"))
// 		// }

// 		cur_frm.cscript.generate_stock = function(doc) {

// 			// mengambil data shopee dan tokped
// 			let all_warehouse = cur_frm.doc.nama_warehouse_shopee
// 			let result = []
// 			frappe.db.get_list('Marketplace Item Shopee',{ filters: {'status_sync': 'yes', 'warehouse': all_warehouse, 'bobot': ['>',0]}, fields: ['name', 'nama_product', 'item_code', 'shop_name','shopee_product_id','warehouse','bobot']})
// 			.then(data => {
				
				
// 				//memasukkan data ke tabel items
// 				if(data.length > 0 ) {

// 					for (let i = 0; i < data.length; i++) {
// 						result.push({
// 							bobot: data[i].bobot,
// 							item_code: data[i].item_code,
// 							nama_product: data[i].nama_product,
// 							item_code_2: data[i].name,
// 							shop_name: data[i].shop_name,
// 							shopee_product_id: data[i].shopee_product_id,
// 							warehouse: data[i].warehouse,
// 							marketplace: 'Shopee'
// 						})
// 					}
					
// 					cur_frm.clear_table("items")
// 					cur_frm.refresh_fields()
// 					for (let i = 0; i < data.length; i++) {
// 						let childTable = cur_frm.add_child("items");
// 						childTable.item_code_2 = data[i].name
// 						childTable.item_name = data[i].nama_product
// 						childTable.item_code = data[i].item_code
// 						childTable.shop_name = data[i].shop_name
// 						childTable.product_id = data[i].shopee_product_id
// 						childTable.warehouse = data[i].warehouse
// 						childTable.bobot = data[i].bobot
// 						childTable.marketplace = 'Shopee'
// 					}
// 					cur_frm.refresh_fields("items")
// 				} else {
// 					cur_frm.clear_table("items")
// 					cur_frm.refresh_fields()
// 					frappe.msgprint("Tidak ada data marketplace item shopee dengan warehouse tersebut / bobot tidak lebih dari 0")
// 				}

// 				return frappe.db.get_list('Marketplace Item Tokopedia',{ filters: {'warehouse': all_warehouse, 'bobot': ['>',0]}, fields: ['name', 'item_name', 'item_code', 'shop','bobot']})
// 			})
// 			.then(data2 => {
				

// 				// memasukkan data ke tabel item tokopedia
// 				if(data2.length > 0 ) {
// 					for (let i = 0; i < data2.length; i++) {
// 						result.push({
// 							bobot: data2[i].bobot,
// 							item_code: data2[i].item_code,
// 							item_name: data2[i].item_name,
// 							name: data2[i].name,
// 							shop: data2[i].shop,
// 							marketplace: 'Tokopedia'
// 						})
// 					}


// 					cur_frm.clear_table("item_stock_tokopedia")
// 					cur_frm.refresh_fields()
// 					for (let i = 0; i < data2.length; i++) {
// 						let childTable = cur_frm.add_child("item_stock_tokopedia");
// 						childTable.marketplace_item_tokopedia = data2[i].name
// 						childTable.item_name = data2[i].item_name
// 						childTable.item_code = data2[i].item_code
// 						childTable.shop_name = data2[i].shop
// 						childTable.sku = data2[i].item_code
// 						childTable.bobot = data2[i].bobot
// 						childTable.marketplace = 'Tokopedia'
// 					}
// 					cur_frm.refresh_fields("item_stock_tokopedia")
// 				} else {
// 					cur_frm.clear_table("item_stock_tokopedia")
// 					cur_frm.refresh_fields()
// 					// cur_frm.save();
// 					frappe.msgprint("Tidak ada data marketplace item Tokopedia dengan warehouse tersebut / bobot tidak lebih dari 0")
// 				}
// 			})

// 			setTimeout(() => {
// 				let all_product = result
// 				let items = []
// 				var allTotalStock = []
// 				let result2 = all_product.reduce((a, v) => (( a[v.item_code] = a[v.item_code] || [] ).push(v), a ), {})
		
				
// 				for (let i = 0; i < all_product.length; i++) {
// 					items.push(all_product[i].item_code)
// 				}
				
// 				// mengambil itemcode yg unique
// 				let uniqueItems = [...new Set(items)]

// 				// mengambil semua stock item sesuai warehouse
// 				for (let j = 0; j < uniqueItems.length; j++) {		
// 					frappe.db.get_list('Bin',{ filters: {'item_code': uniqueItems[j], 'warehouse': all_warehouse}, fields: 'actual_qty'})
// 					.then(data => {
// 						if (data.length > 0) {
// 							let totalStock = 0
// 							for ( let m = 0; m < data.length; m++) {
// 								totalStock += data[m].actual_qty
// 							}

// 							allTotalStock.push({
// 								item: uniqueItems[j],
// 								warehouse: all_warehouse,
// 								totalStock: totalStock
// 							})
// 						}

// 					})
// 				}
				
// 				let value = Object.values(result)

// 				setTimeout(() => {

// 					// memasukkan semua bobot
// 					let allBobot = []
// 					for (let key in result2) {
// 						let temp = 0
// 						for (let i = 0; i < result2[key].length; i++) {
// 							temp += Number(result2[key][i].bobot)
// 						}
// 						allBobot.push(temp)
// 					}

// 					// sort result
// 					for (let key in result2) {
// 						result2[key].sort((a,b) => (a.bobot < b.bobot) ? 1 : ((b.bobot < a.bobot) ? -1 : 0))
// 					}


// 					// memasukkan new stock
// 					let counter = 0
// 					let finalResult = []
// 					for (let key in result2) {
// 						let temp = []
// 						let stockExist = 0
// 						for (let i = 0; i < result2[key].length; i++) {
// 							if (i == result2[key].length-1) {
// 								let hasil2 = allTotalStock[counter].totalStock - stockExist
// 								if(result2[key][i].marketplace == 'Shopee') {
// 									temp.push({
// 										name: result2[key][i].nama_product,
// 										item_code: result2[key][i].item_code,
// 										product_id: result2[key][i].shopee_product_id,
// 										new_stock: Math.ceil(hasil2),
// 										marketplace_id: result2[key][i].item_code_2,
// 										marketplace: 'Shopee'
// 									})
// 								} else {
// 									temp.push({
// 										name: result2[key][i].item_name,
// 										item_code: result2[key][i].item_code,
// 										sku: result2[key][i].item_code,
// 										new_stock: Math.ceil(hasil2),
// 										marketplace_id: result2[key][i].name,
// 										marketplace: 'Tokopedia'
// 									})
// 								}
								
// 							} else {
// 								let hasil = (Number(result2[key][i].bobot)*allTotalStock[counter].totalStock)/allBobot[counter]
// 								stockExist += Math.ceil(hasil)
// 								if(result2[key][i].marketplace == 'Shopee') {
// 									temp.push({
// 										name: result2[key][i].nama_product,
// 										item_code: result2[key][i].item_code,
// 										product_id: result2[key][i].shopee_product_id,
// 										new_stock: Math.ceil(hasil),
// 										marketplace_id: result2[key][i].item_code_2,
// 										marketplace: 'Shopee'
// 									})
// 								} else {
// 									temp.push({
// 										name: result2[key][i].item_name,
// 										item_code: result2[key][i].item_code,
// 										sku: result2[key][i].item_code,
// 										new_stock: Math.ceil(hasil),
// 										marketplace_id: result2[key][i].name,
// 										marketplace: 'Tokopedia'
// 									})
// 								}
// 							}
							
// 						}
// 						finalResult.push(temp)
// 						counter++
// 					}
// 					let finalData = []
// 					for (let i = 0; i < finalResult.length; i++) {
// 						for (let j = 0; j < finalResult[i].length; j++) {
// 							finalData.push(finalResult[i][j])
// 						}
// 					}

// 					// memasukkan data ke table
// 					$.each(frm.doc.items || [], function(i, v) {
// 						for (let i = 0; i < finalData.length; i++) {
// 							if (finalData[i].marketplace_id == v.item_code_2 && finalData[i].marketplace == v.marketplace) {
// 								frappe.model.set_value(v.doctype, v.name, "new_stock", finalData[i].new_stock)
// 							}
// 						}
// 					})
// 					frm.refresh_field('items')

// 					$.each(frm.doc.item_stock_tokopedia || [], function(i, v) {
// 						for (let i = 0; i < finalData.length; i++) {
// 							if (finalData[i].marketplace_id == v.marketplace_item_tokopedia && finalData[i].marketplace == v.marketplace) {
// 								frappe.model.set_value(v.doctype, v.name, "new_stock", finalData[i].new_stock)
// 							}
// 						}
// 					})
					
// 					frm.refresh_field('item_stock_tokopedia')
// 					cur_frm.save();
					
// 				},1000)

// 			},1000)
// 			// if (cur_frm.doc.marketplace == 'Shopee' ) {
// 			// 	// cur_frm.save()
// 			// 	// if (cur_frm.doc.items.length > 0) {
// 			// 		let all_warehouse = cur_frm.doc.nama_warehouse_shopee
// 			// 		frappe.db.get_list('Marketplace Item Shopee',{ filters: {'status_sync': 'yes', 'warehouse': all_warehouse, 'bobot': ['>',0]}, fields: ['name', 'nama_product', 'item_code', 'shop_name','shopee_product_id','warehouse','bobot']})
// 			// 		.then(data => {
// 			// 			if(data.length > 1 ) {
// 			// 				cur_frm.clear_table("items")
// 			// 				cur_frm.refresh_fields()
// 			// 				for (let i = 0; i < data.length; i++) {
// 			// 					let childTable = cur_frm.add_child("items");
// 			// 					childTable.item_code_2 = data[i].name
// 			// 					childTable.item_name = data[i].nama_product
// 			// 					childTable.item_code = data[i].item_code
// 			// 					childTable.shop_name = data[i].shop_name
// 			// 					childTable.product_id = data[i].shopee_product_id
// 			// 					childTable.warehouse = data[i].warehouse
// 			// 					childTable.bobot = data[i].bobot
// 			// 				}
// 			// 				cur_frm.refresh_fields("items")
							
							
// 			// 				let all_product = cur_frm.doc.items
// 			// 				let items = []
// 			// 				var allTotalStock = []
// 			// 				let result = all_product.reduce((a, v) => (( a[v.item_code] = a[v.item_code] || [] ).push(v), a ), {})
					
					
// 			// 				for (let i = 0; i < all_product.length; i++) {
// 			// 					items.push(all_product[i].item_code)
// 			// 				}
					
// 			// 				let uniqueItems = [...new Set(items)]
					
							
// 			// 				for (let j = 0; j < uniqueItems.length; j++) {
								
// 			// 					let itemStock = frappe.db.get_list('Bin',{ filters: {'item_code': uniqueItems[j], 'warehouse': all_warehouse}, fields: 'actual_qty'})
// 			// 					.then(data => {
									
// 			// 						if (data.length > 0) {
// 			// 							let totalStock = 0
// 			// 							for ( let m = 0; m < data.length; m++) {
// 			// 								totalStock += data[m].actual_qty
// 			// 							}
				
// 			// 							allTotalStock.push({
// 			// 								item: uniqueItems[j],
// 			// 								warehouse: all_warehouse,
// 			// 								totalStock: totalStock
// 			// 							})
// 			// 						}
				
// 			// 					})
								
								
// 			// 				}
							
							
// 			// 				let value = Object.values(result)
					
// 			// 				let temp = []
// 			// 				for (let i = 0; i < value.length; i++) {
// 			// 					let oke = []
// 			// 					for (let j = 0; j < value[i].length; j++) {
// 			// 						oke.push(value[i][j].item_code)
// 			// 					}
// 			// 					temp.push(oke)
// 			// 				}	
							
// 			// 				setTimeout(() => {
// 			// 					let allBobot = []
// 			// 					for (let key in result) {
// 			// 						let temp = 0
// 			// 						for (let i = 0; i < result[key].length; i++) {
// 			// 							temp += Number(result[key][i].bobot)
// 			// 						}
// 			// 						allBobot.push(temp)
// 			// 					}
					
// 			// 					// sort result
// 			// 					for (let key in result) {
// 			// 						result[key].sort((a,b) => (a.bobot < b.bobot) ? 1 : ((b.bobot < a.bobot) ? -1 : 0))
// 			// 					}
					
// 			// 					let counter = 0
// 			// 					let coba = []
// 			// 					for (let key in result) {
// 			// 						let temp = []
// 			// 						let stockExist = 0
// 			// 						for (let i = 0; i < result[key].length; i++) {
// 			// 							if (i == result[key].length-1) {
// 			// 								let hasil2 = allTotalStock[counter].totalStock - stockExist
// 			// 								temp.push({
// 			// 									name: result[key][i].item_name,
// 			// 									item_code: result[key][i].item_code,
// 			// 									product_id: result[key][i].product_id,
// 			// 									new_stock: Math.ceil(hasil2),
// 			// 									marketplace_id: result[key][i].item_code_2
// 			// 								})
// 			// 							} else {
// 			// 								let hasil = (Number(result[key][i].bobot)*allTotalStock[counter].totalStock)/allBobot[counter]
					
// 			// 								stockExist += Math.ceil(hasil)
// 			// 								temp.push({
// 			// 									name: result[key][i].item_name,
// 			// 									item_code: result[key][i].item_code,
// 			// 									product_id: result[key][i].product_id,
// 			// 									new_stock: Math.ceil(hasil),
// 			// 									marketplace_id: result[key][i].item_code_2
// 			// 								})
// 			// 							}
										
// 			// 						}
// 			// 						coba.push(temp)
// 			// 						counter++
// 			// 					}
// 			// 					let final_result = []
// 			// 					for (let i = 0; i < coba.length; i++) {
// 			// 						for (let j = 0; j < coba[i].length; j++) {
// 			// 							final_result.push(coba[i][j])
// 			// 						}
// 			// 					}
					
					
// 			// 					// memasukkan data ke table
// 			// 					$.each(frm.doc.items || [], function(i, v) {
// 			// 						for (let i = 0; i < final_result.length; i++) {
// 			// 							if (final_result[i].marketplace_id == v.item_code_2) {
// 			// 								frappe.model.set_value(v.doctype, v.name, "new_stock", final_result[i].new_stock)
// 			// 							}
// 			// 						}
// 			// 					})
								
// 			// 					frm.refresh_field('items')
// 			// 					cur_frm.save();
// 			// 				}, 1000)
// 			// 			} else {
// 			// 				cur_frm.clear_table("items")
// 			// 				cur_frm.refresh_fields()
// 			// 				cur_frm.save();
// 			// 				frappe.msgprint("Tidak ada data marketplace item shopee dengan warehouse tersebut / bobot tidak lebih dari 0")
// 			// 			}
						
// 			// 		})
					
					
					
					
// 			// 	// } 
	
// 			// } else {
// 			// 	if (cur_frm.doc.item_stock_tokopedia.length > 0) {
// 			// 		let all_warehouse = cur_frm.doc.nama_warehouse_shopee
// 			// 		let all_product = cur_frm.doc.item_stock_tokopedia
// 			// 		let items = []
// 			// 		var allTotalStock = []
// 			// 		let result = all_product.reduce((a, v) => (( a[v.item_code] = a[v.item_code] || [] ).push(v), a ), {})


// 			// 		for (let i = 0; i < all_product.length; i++) {
// 			// 			items.push(all_product[i].item_code)
// 			// 		}

// 			// 		let uniqueItems = [...new Set(items)]

// 			// 		for (let k = 0; k < all_warehouse.length; k++) {
// 			// 			for (let j = 0; j < uniqueItems.length; j++) {
							
// 			// 				let itemStock = frappe.db.get_list('Bin',{ filters: {'item_code': uniqueItems[j], 'warehouse': all_warehouse[k].warehouse}, fields: 'actual_qty'})
// 			// 				.then(data => {
								
// 			// 					if (data.length > 0) {
// 			// 						let totalStock = 0
// 			// 						for ( let m = 0; m < data.length; m++) {
// 			// 							totalStock += data[m].actual_qty
// 			// 						}
			
// 			// 						allTotalStock.push({
// 			// 							item: uniqueItems[j],
// 			// 							warehouse: all_warehouse[k].warehouse,
// 			// 							totalStock: totalStock
// 			// 						})
// 			// 					}
			
// 			// 				})
							
							
// 			// 			}
// 			// 		}

// 			// 		let value = Object.values(result)
			
// 			// 		let temp = []
// 			// 		for (let i = 0; i < value.length; i++) {
// 			// 			let oke = []
// 			// 			for (let j = 0; j < value[i].length; j++) {
// 			// 				oke.push(value[i][j].item_code)
// 			// 			}
// 			// 			temp.push(oke)
// 			// 		}	

// 			// 		setTimeout(() => {
// 			// 			let allBobot = []
// 			// 			for (let key in result) {
// 			// 				let temp = 0
// 			// 				for (let i = 0; i < result[key].length; i++) {
// 			// 					temp += Number(result[key][i].bobot)
// 			// 				}
// 			// 				allBobot.push(temp)
// 			// 			}
			
// 			// 			// sort result
// 			// 			for (let key in result) {
// 			// 				result[key].sort((a,b) => (a.bobot < b.bobot) ? 1 : ((b.bobot < a.bobot) ? -1 : 0))
// 			// 			}
			
// 			// 			let counter = 0
// 			// 			let coba = []
// 			// 			for (let key in result) {
// 			// 				let temp = []
// 			// 				let stockExist = 0
// 			// 				for (let i = 0; i < result[key].length; i++) {
// 			// 					if (i == result[key].length-1) {
// 			// 						let hasil2 = allTotalStock[counter].totalStock - stockExist
// 			// 						temp.push({
// 			// 							name: result[key][i].item_name,
// 			// 							item_code: result[key][i].item_code,
// 			// 							sku: result[key][i].sku,
// 			// 							new_stock: Math.ceil(hasil2),
// 			// 							marketplace_id: result[key][i].marketplace_item_tokopedia
// 			// 						})
// 			// 					} else {
// 			// 						let hasil = (Number(result[key][i].bobot)*allTotalStock[counter].totalStock)/allBobot[counter]
			
// 			// 						stockExist += Math.ceil(hasil)
// 			// 						temp.push({
// 			// 							name: result[key][i].item_name,
// 			// 							item_code: result[key][i].item_code,
// 			// 							sku: result[key][i].sku,
// 			// 							new_stock: Math.ceil(hasil),
// 			// 							marketplace_id: result[key][i].marketplace_item_tokopedia
// 			// 						})
// 			// 					}
								
// 			// 				}
// 			// 				coba.push(temp)
// 			// 				counter++
// 			// 			}

// 			// 			let final_result = []
// 			// 			for (let i = 0; i < coba.length; i++) {
// 			// 				for (let j = 0; j < coba[i].length; j++) {
// 			// 					final_result.push(coba[i][j])
// 			// 				}
// 			// 			}
			
			
// 			// 			// memasukkan data ke table
// 			// 			$.each(frm.doc.item_stock_tokopedia || [], function(i, v) {
// 			// 				for (let i = 0; i < final_result.length; i++) {
// 			// 					if (final_result[i].marketplace_id == v.marketplace_item_tokopedia) {
// 			// 						frappe.model.set_value(v.doctype, v.name, "new_stock", final_result[i].new_stock)
// 			// 					}
// 			// 				}
// 			// 			})
						
// 			// 			frm.refresh_field('items')
// 			// 			cur_frm.save();
// 			// 		}, 1000)

// 			// 		// console.log(allTotalStock)
// 			// 	} else {
// 			// 		frappe.throw('Tabel Item Stock harap di isi!')
// 			// 	}
				
// 			// }
// 		}
		
// 	},
// 	on_submit: function(frm) {
		
// 		frappe.call({
// 			method: "marketplace_connector.marketplace_connector.doctype.shopee_shop_setting.shopee_shop_setting.bulkUpdateStock",
// 			args: {
// 				item_data: cur_frm.doc.items
// 			}
// 		})
// 		.then(result => {
// 			return frappe.call({
// 				method: "tokopedia_connector.tokopedia_connector.tokopedia.bulk_update",
// 				args: {
// 					data: cur_frm.doc.item_stock_tokopedia
// 				}
// 			})
// 			.then(data2 => {
// 				frappe.msgprint(result)
// 				frappe.msgprint(data2)
// 			})
// 		})
		
		
	
		
		
		
// 	}
// });
